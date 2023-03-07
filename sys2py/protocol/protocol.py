from sys2py.systems import sutter, doric, injector, system
import os
import pandas as pd


class Protocol:
    '''Class to create and run a protocol that interacts with System objects'''
    def __init__(self, path='', protocol=None, sys_settings=None, verbose=True):

        self.verbose = verbose
        self.sutter = {}
        self.doric = {}
        self.injector = {}

        if os.path.exists(path):
            self.load(path)
            self.init_protocol()
        else:
            self.protocol = protocol
            self.sys_settings = sys_settings
            self.init_protocol()

            if self.protocol is None:
                self.protocol = pd.DataFrame({'system': [],
                                              'coord_type': [],
                                              'coordinates': [],
                                              'duration': []})
            if self.sys_settings is None:
                self.sys_settings = {}

    def load(self, path):
        '''Loads the protocol and sys_settings json files'''
        if os.path.isdir(path):
            protocol_exists = False
            sys_settings_exists = False
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.name.endswith('_protocol.h5'):
                        self.protocol = pd.read_hdf(os.path.join(path, entry.name))
                        protocol_exists = True
                    elif entry.name.endswith('_sys_settings.json'):
                        self.sys_settings = system.load_json(os.path.join(path, entry.name))
                        sys_settings_exists = True

            if not protocol_exists:
                raise FileNotFoundError('protocol.h5 does not exist in directory')
            elif not sys_settings_exists:
                raise FileNotFoundError('sys_settings.json does not exist in directory')
            else:
                if self.verbose:
                    print('protocol and sys_settings are loaded')
        else:
            raise NotADirectoryError('Path is not a folder. Enter the folder that contains the .json files.')

    def init_protocol(self):
        '''Initializes systems in the protocol'''
        if self.protocol is not None and self.sys_settings is not None:
            for name in self.protocol['system'].unique():
                self.init_system(name)
        else:
            if self.verbose:
                print('protocol or sys_settings empty. No system is initialized')

    def init_system(self, name):
        '''Initializes system in the sys_settings'''
        try:
            sys = self.sys_settings[name]
        except KeyError:
            print('System not available is sys_settings. Use add_system to add to sys_settings')

        if sys['system'] in sutter.sutter_systems():
            self.sutter[name] = sutter.Sutter(**sys)
        elif sys['system'] in doric.doric_systems():
            self.doric[name] = doric.Doric(**sys)
        elif sys['system'] in injector.injector_systems():
            self.injector[name] = injector.Injector(**sys)
        else:
            raise ValueError(f'{sys["system"]} system not available.')

        if self.verbose:
            print(f'Initialized system {name}')

    def save(self, dir, file_root):
        '''Saves the protocol and sys_settings as json files
        dir: path to directory where the json files will be saved in
        file_root: file name root for the json files.
        '_protocol.json' and '_sys_settings.json' are added to the file_root before saving'''
        if os.path.isdir(dir):
            prot_path = os.path.join(dir, file_root + '_protocol.h5')
            sys_sett_path = os.path.join(dir, file_root + '_sys_settings.json')
            self.protocol.to_hdf(prot_path, 'protocol', 'w')
            with open(sys_sett_path, 'w') as out_s:
                json.dump(self.sys_settings, out_s)

            if self.verbose:
                print(f'Saved {prot_path}')
                print(f'Saved {sys_sett_path}')
        else:
            raise NotADirectoryError('dir is not a folder. Enter the folder that will contain the .json files.')

    def add_system(self, path, overwrite=False):
        '''Add system dictionary to the sys_settings'''
        sys = system.load_json(path)
        name = sys['name']
        if name in self.sys_settings.keys():
            if not overwrite:
                raise ValueError(f'The name {name} already exists. Use another system name or set overwrite to True.')
            else:
                if self.verbose:
                    print(f'Overwriting the existing system \'{name}\'')
                self.sys_settings[name] = sys
                self.init_system(name)
        else:
            self.sys_settings[name] = sys
            self.init_system(name)
