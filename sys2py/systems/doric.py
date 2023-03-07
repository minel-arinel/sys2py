from .system import *


class Doric(System):
    '''Class to control the Doric LED fiber light source'''
    def __init__(self, path='', **kwargs):
        '''path: json file path for the system settings
            nChannels: number of channels
            wavelength: channel wavelength in nm
            minCurrent: minimum driving current in mA
            maxCurrent: maximum driving current in mA
            currPerVolt: driving current per analog input voltage in mA/V'''

        if os.path.exists(path):
            kwargs = load_json(path)
            super().__init__(**kwargs)

            self.nChannels = kwargs['nChannels']
            self.wavelength = kwargs['wavelength']
            self.minCurrent = kwargs['minCurrent']
            self.maxCurrent = kwargs['maxCurrent']
            self.currPerVolt = kwargs['currPerVolt']
        else:
            super().__init__(**kwargs)

            systems = doric_systems()

            if System.check_system(self, systems):
                self.nChannels = systems[self.system]['nChannels']
                self.wavelength = systems[self.system]['wavelength']
                self.minCurrent = systems[self.system]['minCurrent']
                self.maxCurrent = systems[self.system]['maxCurrent']
                self.currPerVolt = systems[self.system]['currPerVolt']


def doric_systems(df=False):
    '''Returns dictionary of available Doric systems'''
    systems = {
        'LEDFLS_595': {'nChannels': 1, 'wavelength': 595, 'minCurrent': 18, 'maxCurrent': 1000, 'currPerVolt': 400}
    }

    if not df:
        return systems
    else:
        return pd.DataFrame(systems).transpose()
