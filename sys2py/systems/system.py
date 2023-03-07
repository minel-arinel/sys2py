from serial.tools import list_ports
import serial
import pyfirmata
import json
import os
import pandas as pd


class System:
    '''Class to control external systems that are connected to the computer'''
    def __init__(self, name, system, port, arduino=False, pin_defs=None, verbose=True, **kwargs):

        self.name = name
        self.system = system
        self.arduino = arduino
        self.verbose = verbose

        if 'arduino' in port.lower():
            self.arduino = True

        self.port = port
        if 'COM' not in self.port:
            self.port = self.detect_port()

        if self.arduino:  # if it is connected to an arduino
            try:
                self.board = pyfirmata.Arduino(self.port)
                if self.verbose:
                    print(self.board)

                if len(pin_defs) > 0:
                    self.pins = []
                    self.pin_defs = pin_defs

                    for pin_def in self.pin_defs:
                        if len(pin_def) == 5:
                            pin = self.board.get_pin(pin_def)
                            self.pins.append(pin)

                            if pin_def[-1] == 'i':
                                it = pyfirmata.util.Iterator(self.board)
                                it.start()

                            if self.verbose:
                                print(pin)
                        else:
                            raise ValueError('Arduino pin is not valid. Run arduino_pin_help() for help.')

                else:
                    raise ValueError('Argument pins (list) is empty. Send pin_defs in a list')

            except serial.SerialException:
                print('No connection could be established. Restart the kernel.')
                sys.exit(1)

        else:  # if it is connected directly to the computer
            if 'serial' in kwargs:
                kwargs = kwargs['serial']

            try:
                baudrate = kwargs['baudrate']
                bytesize = kwargs['bytesize']
                parity = kwargs['parity']
                stopbits = kwargs['stopbits']
                timeout = kwargs['timeout']
                xonxoff = kwargs['xonxoff']
                rtscts = kwargs['rtscts']
                write_timeout = kwargs['write_timeout']
                dsrdtr = kwargs['dsrdtr']
                inter_byte_timeout = kwargs['inter_byte_timeout']
                exclusive = kwargs['exclusive']
            except KeyError:
                print('Missing arguments for Serial connection')
                sys.exit(1)

            try:
                self.serial = serial.Serial(port=self.port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff=xonxoff, rtscts=rtscts, write_timeout=write_timeout, dsrdtr=dsrdtr, inter_byte_timeout=inter_byte_timeout, exclusive=exclusive)
                if self.verbose:
                    print(self.serial)
            except serial.SerialException:
                print('No connection could be established. Restart the kernel.')
                sys.exit(1)

    def destroy(self):
        '''Destroys the connection to the system'''
        if self.arduino:
            self.board.exit()
        else:
            self.serial.close()

        if self.verbose:
            print('Connection to the system closed')

    def check_system(self, systems, show=False):
        '''Checks if the system-specific settings are available'''
        if show:
            pd.DataFrame(systems)

        if self.system not in systems.keys():
            print(f'System currently not supported. Please select from the following: {systems.keys()}')
            sys.exit(1)
        else:
            return True

    def detect_port(self):
        '''Returns the port with the given name'''
        port_info = list_ports.grep(self.port)
        ports = [port.device for port in port_info]
        if len(ports) == 0:
            raise FileNotFoundError('Port name not found')
        elif len(ports) > 1:
            raise ValueError('More than one port found. Specify the port.')
        elif len(ports) == 1:
            return ports[0]

    def serial_attributes(self, attrs=list()):
        '''Returns Serial attributes as a dictionary
        attrs: list of attributes'''
        if len(attrs) == 0:
            attrs = ['_port', '_baudrate', '_bytesize', '_parity', '_stopbits',
                     '_timeout', '_xonxoff', '_rtscts', '_write_timeout',
                     '_dsrdtr', '_inter_byte_timeout', '_exclusive']
        ser = self.serial.__dict__
        ser_attrs = dict((attr[1:], ser[attr]) for attr in attrs if attr in ser)
        return ser_attrs

    def save(self, path):
        '''Saves the System object as a json file'''
        if path.endswith('.json'):
            with open(path, 'w') as outfile:
                sys_dict = self.__dict__.copy()

                if 'serial' in sys_dict.keys():
                    sys_dict['serial'] = self.serial_attributes()
                if self.arduino:
                    sys_dict.pop('board')
                    sys_dict.pop('pins')

                json.dump(sys_dict, outfile)
                if self.verbose:
                    print(f'Saved System: {path}')
        else:
            raise ValueError('Could not save System. File type must be a .json')


def load_json(path):
    '''Loads dictionary from a json file'''
    if os.path.isdir(path):
        raise IsADirectoryError('Path is a folder. Change path to a .json file')
    elif os.path.isfile(path):
        if path.endswith('.json'):
            with open(path) as file:
                _dict = json.load(file)
                return _dict
        else:
            raise ValueError('File type must be a .json')
    else:
        raise FileNotFoundError('Path does not exist. Enter an existing .json file')


def arduino_pin_help():
    '''Prints help for the Arduino pin syntax required for pyFirmata'''
    print('The Arduino pin syntax has a length of 5 characters:\n'
          '[0]: \'a\' or \'d\'\n'
          '\t\'a\': analog pin\n'
          '\t\'d\': digital pin\n'
          '[1]: \':\'\n'
          '[2]: (int) the pin number\n'
          '[3]: \':\'\n'
          '[4]: \'i\' or \'o\' or \'p\'\n'
          '\t\'i\': input\n'
          '\t\'o\': output\n'
          '\t\'p\': pulse width modulation (pwm)\n'
          'Examples:\n'
          '\'d:13:o\': digital pin 3 set to output mode for writing\n'
          '\'a:1:i\': analog pin 1 set to input mode for reading')
