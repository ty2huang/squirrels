import os
from configparser import ConfigParser
from squirrels import constants as c

_PROFILE_FILE = os.path.join(os.path.expanduser('~'), '.squirrels_profiles.ini')

def _get_config(section_name_to_include=None):
    config = ConfigParser()
    config.read(_PROFILE_FILE)
    if section_name_to_include != None and not config.has_section(section_name_to_include):
        config.add_section(section_name_to_include)
    return config

def get_profiles():
    config = _get_config()
    return {section: dict(config[section]) for section in config.sections()}

class Profile:
    def __init__(self, name):
        self.name = name
    
    def set(self, dialect, conn_url, username, password):
        settings = {
            c.DIALECT: dialect,
            c.CONN_URL: conn_url,
            c.USERNAME: username,
            c.PASSWORD: password
        }
        config = _get_config(self.name)
        for k, v in settings.items():
            config.set(self.name, k, v)
        
        with open(_PROFILE_FILE, 'w') as f:
            config.write(f)

    def get(self):
        config = _get_config(self.name)
        return dict(config[self.name])

    def delete(self):
        config = _get_config()
        section_exists = config.has_section(self.name)
        if section_exists:
            config.remove_section(self.name)
            with open(_PROFILE_FILE, 'w') as f:
                config.write(f)
        return section_exists
