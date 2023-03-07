from .system import *


class Sutter(System):
	'''Class to control the Sutter micromanipulators'''
	def __init__(self, path='', baudrate=128000, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=5, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None, **kwargs):
		'''path: json file path for the system settings
			stepToMicron: conversion factor from microsteps to microns
			micronToStep: conversion factor from microns to microsteps
			micronRange: (x, y, z) ranges in microns
			stepRange: (x, y, z) ranges in microsteps
			speed: (single, dual, triple) axis speed in mm/s or um/ms'''

		if os.path.exists(path):
			kwargs = load_json(path)
			super().__init__(**kwargs)

			self.stepToMicron = kwargs['stepToMicron']
			self.micronToStep = kwargs['micronToStep']
			self.micronRange = kwargs['micronRange']
			self.stepRange = kwargs['stepRange']
			self.speed = kwargs['speed']
		else:
			super().__init__(baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff=xonxoff, rtscts=rtscts, write_timeout=write_timeout, dsrdtr=dsrdtr, inter_byte_timeout=inter_byte_timeout, exclusive=exclusive, **kwargs)

			systems = sutter_systems()

			if System.check_system(self, systems):
				self.stepToMicron = systems[self.system]['stepToMicron']
				self.micronToStep = systems[self.system]['micronToStep']
				self.micronRange = systems[self.system]['micronRange']
				self.stepRange = systems[self.system]['stepRange']
				self.speed = systems[self.system]['speed']

	def speed_settings(self, df=False, speed=-1):
		'''Defines the speed settings
		df: if True, returns a pandas DataFrame
		speed: if specified, returns a dictionary of its settings'''

		speeds = {
			0: {'mm/s': 0.08125, '%max': 6.25},
			1: {'mm/s': 0.16250, '%max': 12.50},
			2: {'mm/s': 0.24375, '%max': 18.75},
			3: {'mm/s': 0.32500, '%max': 25.00},
			4: {'mm/s': 0.40625, '%max': 31.25},
			5: {'mm/s': 0.48750, '%max': 37.50},
			6: {'mm/s': 0.56875, '%max': 43.75},
			7: {'mm/s': 0.65000, '%max': 50.00},
			8: {'mm/s': 0.73125, '%max': 56.25},
			9: {'mm/s': 0.81250, '%max': 62.50},
			10: {'mm/s': 0.89375, '%max': 68.75},
			11: {'mm/s': 0.97500, '%max': 75.00},
			12: {'mm/s': 1.05625, '%max': 81.25},
			13: {'mm/s': 1.13750, '%max': 87.50},
			14: {'mm/s': 1.21875, '%max': 93.75},
			15: {'mm/s': 1.30000, '%max': 100.00}
		}
		for i in speeds.values():
			i['um/s'] = i['mm/s'] * 1000
			i['nm/s'] = i['mm/s'] * 1000000

		if speed == -1:
			if df:
				return pd.DataFrame(speeds).transpose()
			else:
				return speeds
		elif self.speed_inrange(speed):
			return speeds[speed]

	@staticmethod
	def speed_inrange(speed):
		'''Checks if the speed is within the system range'''
		if speed not in range(16):
			raise ValueError('Speed must be in range [0-15]')
		else:
			return True

	def get_version(self):
		'''Returns major and minor version number'''
		self.serial.write(b'K')
		version = self.serial.read(4)
		if len(version) == 4:
			if self.verbose:
				print(f'Version: {version[2]}.{version[1]}')
			return version[2], version[1]
		else:
			print('Version < 3. Returning 1.0')
			return 1, 00

	def get_active_device(self):
		'''Returns the active device'''
		self.serial.write(b'K')
		device = self.serial.read(1)
		if self.verbose:
			print(f'Active device: {device[0]}')
		return device[0]

	def get_connected_devices(self):
		'''Returns the number of connected devices'''
		major, _ = self.get_version()
		num_devices = 0

		if major >= 3:
			self.serial.write(b'U')
			devices = self.serial.read(6)
			if len(devices) > 0:
				num_devices = devices[0]
			else:
				print('No manipulator connected')

		elif major < 3:
			self.serial.write(b'A')
			devices = self.serial.read(2)
			if len(devices) > 0:
				num_devices = devices[0]
			else:
				print('No manipulator connected')

		if self.verbose:
			print(f'NUmber of connected devices: {num_devices}')
		return num_devices

	def get_current_pos(self, in_microns=True):
		'''Returns a tuple of current (x, y, z) positions
		If inMicrons is True, converts usteps to microns'''
		self.serial.write(b'C')
		_pos = self.serial.read_until(b'\r')
		_x = int.from_bytes(_pos[1:5], 'little')
		_y = int.from_bytes(_pos[5:9], 'little')
		_z = int.from_bytes(_pos[9:13], 'little')

		if in_microns:
			x = round(_x * self.stepToMicron)
			y = round(_y * self.stepToMicron)
			z = round(_z * self.stepToMicron)
		else:
			x = _x
			y = _y
			z = _z

		if self.verbose:
			print(f'Current position x: {x}, y: {y}, z: {z}')

		return (x, y, z)

	def change_active_device(self, device):
		'''Changes the active device to the given device number
		If successful, returns the device number
		If device is not available, returns 0'''
		self.serial.write(bytes(f'I{device}', 'utf-8'))
		changed = self.serial.read(2)
		if changed[0] == 69:
			print('Device does not exist')
			return 0
		elif changed[0] == 13 or changed[0] in range(1, 5):
			if self.verbose:
				print(f'Active device changed to manipulator {device}')
			return device

	def calibrate(self):
		'''If the system version is above 1.03, calibrates the device'''
		major, minor = self.get_version()
		if major >= 1 and minor > 3:
			self.serial.write(b'N')
			self.serial.read_until(b'\r')
			if self.verbose:
				print(f'Calibrated the device')
		else:
			print(f'Cannot calibrate the device. Needs version higher than 1.03. Current version: {major}.{minor}')

	def move_to_home(self):
		'''Moves to Home position defined on the ROE-200'''
		self.serial.write(b'H')
		self.serial.read_until(b'\r')
		if self.verbose:
			print(f'Moved to Home position')

	def set_work_pos(self, pos=(0, 0, 0)):
		'''If a pos is given, sets the coordinates as work position
		If no pos coordinates are entered, sets the current position as the work position
		pos: (x, y, z) coordinates in microns'''
		if pos == (0, 0, 0):
			print('Setting current position as the work position...')
			self.workPos = self.get_current_pos()
		else:
			if self.pos_in_range(pos):
				self.workPos = pos
		if self.verbose:
			print(f'Set work position as {self.workPos}')

	def move_to_work(self, ROE=False):
		'''Moves to Work position
		ROE: if True, moves to work position defined on the ROE-200'''
		if ROE:
			self.serial.write(b'Y')
			self.serial.read_until(b'\r')
			if self.verbose:
				print(f'Moved to Work position')
		else:
			try:
				self.move_to_pos(self.workPos)
			except AttributeError as e:
				print(f'{e}\nNo work position has been defined. Use the set_work_pos function to define a work position')

	def move_to_center(self):
		'''Moves to the center position (midpoint of all x-y-z axes)'''
		x, y, z = self.micronRange
		self.move_to_pos((x/2, y/2, z/2))

	def pos_in_range(self, pos):
		'''Checks if the position coordinates are within the system range'''
		if len(pos) != 3:
			raise ValueError('Need to send all (x, y, z) coordinates as a tuple or list')

		if any(_ < 0 for _ in pos):
			raise ValueError('Position coordinates must be non-negative')
		elif pos[0] > self.micronRange[0]:
			raise ValueError(f'x coordinate out of range. Maximum position is {self.micronRange[0]}')
		elif pos[1] > self.micronRange[1]:
			raise ValueError(f'y coordinate out of range. Maximum position is {self.micronRange[1]}')
		elif pos[2] > self.micronRange[2]:
			raise ValueError(f'z coordinate out of range. Maximum position is {self.micronRange[2]}')
		else:
			return True

	def move_to_pos(self, pos, straight=False, speed=0):
		'''Moves to the given position coordinates
		pos: (x, y, z) coordinates of target position
		straight: False for orthogonal movement at full speed. True for straight line movement at specified speed
		speed: Speed setting for straight movement. Values [0-15]'''
		if self.pos_in_range(pos):
			_x = round(pos[0] * self.micronToStep)
			_y = round(pos[1] * self.micronToStep)
			_z = round(pos[2] * self.micronToStep)
			_pos = _x.to_bytes(4, 'little') + \
				   _y.to_bytes(4, 'little') + \
				   _z.to_bytes(4, 'little')

		self.serial.write(b'M' + _pos + b'\r')
		self.serial.read_until(b'\r')

		'''if not straight:
			self.serial.write(b'M' + _pos + b'\r')
			self.serial.read_until(b'\r')'''

		'''else:
			if self.get_version()[0] < 3:
				raise ValueError('System does not support straight line movements. Requires version 3+. Set straight to False')
			else:
				if self.speed_inrange(speed):
					_s = speed.to_bytes(1, 'little')
					self.serial.write(b'S' + _s)
					time.sleep(0.03)
					self.serial.write(_pos)
					self.serial.read_until(b'\r')'''

		if self.verbose:
			print(f'Moved to {pos}')

	def move_to_relative_pos(self, pos):
		'''Moves to the given position coordinates relative to the current position
		pos: (dx, dy, dz) change in coordinates in microns'''
		x, y, z = self.get_current_pos()
		_pos = (x+pos[0], y+pos[1], z+pos[2])
		self.move_to_pos(_pos)

	def interrupt_move(self):
		'''Interrupts a move in progress originating from an external command'''
		self.serial.write(b'^C')
		self.serial.read_until(b'\r')
		if self.verbose:
			print('Interrupted move')

	def set_ROE_mode(self, mode):
		'''Sets ROE mode
		mode: Values [0-9]'''
		if mode not in range(10):
			raise ValueError('ROE mode must be in range [0-9]')

		_m = mode.to_bytes(1, 'little')
		self.serial.write(b'L' + _m)
		self.serial.read_until(b'\r')
		if self.verbose:
			print(f'Set ROE mode to {mode}')

	def reset_x(self):
		'''Moves to 0 on the x-axis'''
		_, y, z = self.get_current_pos()
		self.move_to_pos((0, y, z))

	def reset_y(self):
		'''Moves to 0 on the y-axis'''
		x, _, z = self.get_current_pos()
		self.move_to_pos((x, 0, z))

	def reset_z(self):
		'''Moves to 0 on the z-axis'''
		x, y, _ = self.get_current_pos()
		self.move_to_pos((x, y, 0))


def sutter_systems(df=False):
	'''Returns dictionary of available Sutter systems'''
	systems = {
		'MP-865': {'stepToMicron': 0.046875, 'micronToStep': 21.333333333, 'micronRange': (50000, 12500, 25000),
				   'stepRange': (533334, 133334, 266667), 'speed': (3, 4.2, 5.1)},
		'MP-245': {'stepToMicron': 0.046875, 'micronToStep': 21.333333333, 'micronRange': (25000, 25000, 25000),
				   'stepRange': (266667, 266667, 266667), 'speed': (3, 4.2, 5.1)},
		'MP-845': {'stepToMicron': 0.046875, 'micronToStep': 21.333333333, 'micronRange': (25000, 25000, 25000),
				   'stepRange': (266667, 266667, 266667), 'speed': (3, 4.2, 5.1)},
		'MP-265': {'stepToMicron': 0.0625, 'micronToStep': 16, 'micronRange': (25000, 12500, 25000),
				   'stepRange': (400000, 200000, 400000), 'speed': (5, 7, 8.5)},
		'MP-285': {'stepToMicron': 0.0625, 'micronToStep': 16, 'micronRange': (25000, 25000, 25000),
				   'stepRange': (400000, 400000, 400000), 'speed': (5, 7, 8.5)},
		'MP-225': {'stepToMicron': 0.0625, 'micronToStep': 16, 'micronRange': (25000, 25000, 25000),
				   'stepRange': (400000, 400000, 400000), 'speed': (3, 4.2, 5.1)}
	}

	if not df:
		return systems
	else:
		return pd.DataFrame(systems).transpose()
