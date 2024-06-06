from configparser import ConfigParser, DuplicateSectionError, NoOptionError
import time
import os


class Settings:
    SETTINGS_FILE_NAME = 'config.ini'

    def __init__(self):
        self.settings = ConfigParser()
        self.settings.read(self.SETTINGS_FILE_NAME)
        try:
            self.settings.add_section('General')
        except DuplicateSectionError:
            pass
        # Check for configuration file existence
        if not os.path.exists(self.SETTINGS_FILE_NAME):
            self.set_defaults()
        # Check if configuration file is correct
        try:
            _ = self.temperature_unit
            _ = self.date_format
            _ = self.time_format
            _ = self.timezone
            _ = self.dst
            _ = self.auto_download
            _ = self.time_standard
        except NoOptionError:
            print('Configuration file is corrupted. Restoring it by defaults')
            self.set_defaults()

    def update(self):
        self.settings.read(self.SETTINGS_FILE_NAME)

    def save(self):
        with open(self.SETTINGS_FILE_NAME, 'w') as f:
            self.settings.write(f)

    def set_defaults(self):
        self.temperature_unit = 0
        self.date_format = 0
        self.time_format = 0
        self.timezone = -time.timezone
        self.dst = 0
        self.auto_download = 1
        self.time_standard = 0
        self.save()

    @property
    def temperature_unit(self):
        return int(self.settings.get('General', 'Temperature unit'))

    @temperature_unit.setter
    def temperature_unit(self, value):
        self.settings.set('General', 'Temperature unit', str(value))

    @property
    def date_format(self):
        return int(self.settings.get('General', 'Date format'))

    @date_format.setter
    def date_format(self, value):
        self.settings.set('General', 'Date format', str(value))

    @property
    def time_format(self):
        return int(self.settings.get('General', 'Time format'))

    @time_format.setter
    def time_format(self, value):
        self.settings.set('General', 'Time format', str(value))

    @property
    def timezone(self):
        return int(self.settings.get('General', 'Timezone'))

    @timezone.setter
    def timezone(self, value):
        self.settings.set('General', 'Timezone', str(value))

    @property
    def dst(self):
        return bool(int(self.settings.get('General', 'DST')))

    @dst.setter
    def dst(self, value):
        self.settings.set('General', 'DST', str(int(value)))

    @property
    def auto_download(self):
        return bool(int(self.settings.get('General', 'Auto download')))

    @auto_download.setter
    def auto_download(self, value):
        self.settings.set('General', 'Auto download', str(int(value)))

    @property
    def time_standard(self):
        return int(self.settings.get('General', 'Time standard'))

    @time_standard.setter
    def time_standard(self, value):
        self.settings.set('General', 'Time standard', str(value))
