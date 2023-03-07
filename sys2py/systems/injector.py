from .system import *


class Injector(System):
    '''Class to control the injectors'''
    def __init__(self, path='', **kwargs):
        '''path: json file path for the system settings
            ttlOn: TTL signal that initiates injection (0 or 1)'''

        if os.path.exists(path):
            kwargs = load_json(path)
            super().__init__(**kwargs)

            self.ttlOn = kwargs['ttlOn']

        else:
            super().__init__(**kwargs)

            systems = injector_systems()

            if System.check_system(self, systems):
                self.ttlOn = systems[self.system]['ttlOn']


def injector_systems(df=False):
    '''Returns dictionary of available Injector systems'''
    systems = {
        'Metcal': {'ttlOn': 1},
        'PV850': {'ttlOn': 0}
    }

    if not df:
        return systems
    else:
        return pd.DataFrame(systems).transpose()
