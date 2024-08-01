import yaml
import os

class _Config:
    # From : https://stackoverflow.com/questions/48351139/loading-config-from-class-in-such-a-way-that-it-behaves-like-a-property
    def __init__(self):
        """ Load the config file and parse the command line arguments. File takes precedence"""
        with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as yaml_config_file:
            self.config = yaml.safe_load(yaml_config_file)
    
    def __getattr__(self, name):
        try:
            return self.config[name]
        except KeyError:
            return getattr(self.args, name)


config = _Config()
