import pandas as pd
import numpy as np
from system import *
import os
import json


class Protocol:
    '''Class to create and run a protocol that interacts with System objects'''
    def __init__(self, path='', protocol=dict(), sys_settings=dict(), verbose=True):

        self.verbose = verbose

        if os.path.exists(path):
            self.load(path)
        else:
            self.sys_settings = sys_settings
            self.protocol = protocol
            if len(self.protocol) == 0:
                self.protocol = {'system': [],
                                 'coord_type': [],
                                 'coordinates': [],
                                 'duration': []}














    def preview_path(self):
        '''Moves the manipulator along the protocol coordinates'''
        if isinstance(self.sutter, Sutter):
            start = self.sutter.get_current_pos()
            df = self.protocol_df()
            sutter_df = df[df['system'] == 'sutter']
            for i, row in sutter_df.iterrows():
                if row['coord_type'] == 'abs':
                    self.sutter.move_to_pos(row['coordinates'])
                elif row['coord_type'] == 'rel':
                    self.sutter.move_to_relative_pos(row['coordinates'])
            self.sutter.move_to_pos(start)
        else:
            self.sutter_error()

    def protocol_df(self):
        '''Returns the protocol attribute as a pandas DataFrame'''
        return pd.DataFrame(self.protocol)

    def save(self, path):
        '''Saves the protocol and sys_settings as json files'''
        save_json(self.protocol, os.path.join(path, 'protocol.json'), self.verbose)
        save_json(self.sys_settings, os.path.join(path, 'sys_settings.json'), self.verbose)

    def load(self, path):
        '''Loads the protocol and sys_settings from json files'''
        self.protocol = load_json(os.path.join(path, 'protocol.json'))
        self.sys_settings = load_json(os.path.join(path, 'sys_settings.json'))
        for sys in self.sys_settings:
            self.run_system(sys)


def save_json(_dict, path, verbose=True):
    '''Saves dictionary as a json file'''
    if path.endswith('.json'):
        with open(path, 'w') as outfile:
            json.dump(_dict, outfile)
            if verbose:
                print(f'Saved {path}')
            outfile.close()
    else:
        raise ValueError('Could not save dictionary. File type must be a .json')


def load_json(path):
    '''Loads dictionary from a json file'''
    if path.endswith('.json'):
        with open(path) as file:
            return json.load(file)
    else:
        raise ValueError('Could not load dictionary. File type must be a .json')
