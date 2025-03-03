import json
import os

class Settings:
    def __init__(self, filename='settings.json'):
        ''' init a settings object

        filename: the filename to save the settings
        '''
        self.filename = filename
        self.settings = {
            "last_filename": None,
            "module_ECTS": 5,
            "module_duration": 6
        }
        self.load_settings()

    def load_settings(self):
        ''' load the settings from the file '''
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.settings = json.load(file)
        else:
            self.save_settings()

    def save_settings(self):
        ''' save the settings to the file '''
        with open(self.filename, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key, default=None):
        ''' get a setting by key

        key: the setting key
        default: the default value if the key does not exist
        '''
        return self.settings.get(key, default)

    def set(self, key, value):
        ''' set a setting by key

        key: the setting key
        value: the value to set
        '''
        self.settings[key] = value
        self.save_settings()