"""Module to manage configuration files"""
import os
from configparser import ConfigParser

# pylint: disable-next=too-many-ancestors
class Config(ConfigParser):
    """Manage configuration files"""
    _instance = None
    _original_instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = cls._get_new_instance(*args, **kwargs)
        return cls._instance

    def __init__(self, initialize=False):
        if initialize is True:
            super().__init__(allow_no_value=True)
            self._read_config_files()

    def save(self):
        """Write current data to configuration file"""
        config_changes = self._changes()
        if config_changes is None:
            return

        path = self._get_config_file_paths()[-1]
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(os.path.dirname(path), mode=0o755)
            with open(path, 'w', encoding='utf-8') as config_file:
                config_changes.write(config_file)
            self._original().read_dict(config_changes)
        except (FileNotFoundError, OSError) as exception:
            print(f'Could not save configuration: {exception}')

    def _changes(self):
        changes = {}
        for section_name, section in self.items():
            for option, value in section.items():
                if self._original().get(section_name, option) == value:
                    continue
                if section_name not in changes:
                    changes[section_name] = {}
                changes[section_name][option] = value

        if not bool(changes):
            return None

        config_changes = ConfigParser()
        config_changes.read_dict(changes)
        return config_changes

    def _read_config_files(self):
        paths = self._get_config_file_paths()
        if not self.read(paths):
            self.read(f'{paths[0]}.example')

    @classmethod
    def _get_new_instance(cls, *args, **kwargs):
        instance = object.__new__(cls, *args, **kwargs)
        instance.__init__(initialize=True)
        return instance

    @classmethod
    def _get_config_file_paths(cls):
        return (
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f'{cls._config_name()}.conf',
            ),
            os.path.join(
                os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
                cls._config_name(),
                f'{cls._config_name()}.conf'
            ),
        )

    @classmethod
    def _original(cls):
        if not isinstance(cls._original_instance, cls):
            cls._original_instance = cls._get_new_instance()
        return cls._original_instance

    @staticmethod
    def _config_name():
        """Returns the name of the application"""
        return 'linaktray'
