from .protocol import Protocol


class SutterProtocol(Protocol):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)

    def add_curr_coords(self, name, coord_type, duration=0):
        '''Adds current Sutter position to the protocol coordinates
        name: system name
        coord_type: Can be either 'abs' for absolute coordinates or 'rel' for relative coordinates'''
        curr = self.sutter[name].get_current_pos()
        if self.check_coord_type(coord_type):
            if coord_type == 'abs':
                self.add_abs_coords(curr, duration)
            elif coord_type == 'rel':
                try:
                    prev = self.protocol['coordinates'][-1]
                except IndexError:
                    print('There are no previous coordinates in the protocol. Taking previous coordinate as (0, 0, 0)')
                    prev = (0, 0, 0)
                pos = self.calc_rel_coords(prev, curr)
                self.add_rel_coords(pos, duration)
        else:
            raise ValueError('Could not add coordinates of with incorrect coord_type')

    @staticmethod
    def check_coord_type(coord_type):
        '''Checks if the coord_type is 'abs' or 'rel' '''
        if coord_type != 'abs' and coord_type != 'rel':
            print('Coordinate type must be either \'abs\' for absolute coordinates or \'rel\' for relative coordinates')
            return False
        else:
            return True

    @staticmethod
    def calc_rel_coords(pos1, pos2):
        '''Calculates the relative coordinates between two absolute positions'''
        return (pos2[0] - pos1[0], pos2[1] - pos1[1], pos2[1] - pos1[1])

    def add_coords(self, name, pos, coord_type, duration=0):
        '''Adds the Sutter position coordinates to the protocol
        name: system name
        coord_type: Can be either 'abs' for absolute coordinates or 'rel' for relative coordinates'''
        self.protocol['system'].append(name)
        if self.check_coord_type(coord_type):
            self.protocol['coord_type'].append(coord_type)
        else:
            raise ValueError('Could not add coordinates. Incorrect coord_type')
        self.protocol['coordinates'].append(pos)
        self.protocol['duration'].append(duration)
        if self.verbose:
            print(f'Position of type {coord_type} is added to the protocol: {pos}')

    def add_abs_coords(self, name, pos, duration=0, move=False):
        '''Adds absolute Sutter position to the protocol coordinates'''
        if move:
            try:
                self.sutter[name].move_to_pos(pos)
            except KeyError:
                print(f'Sutter system {name} does not exist')
        self.add_coords(name, pos, 'abs', duration)

    def add_rel_coords(self, name, pos, duration=0, move=False):
        '''Adds relative Sutter position to the protocol coordinates'''
        if move:
            try:
                self.sutter[name].move_to_relative_pos(pos)
            except KeyError:
                print(f'Sutter system {name} does not exist')
        self.add_coords(name, pos, 'rel', duration)


def sutter_error():
    print('Sutter instance not available. Use add_system to initialize it')




