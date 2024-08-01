import yaml
import os

import hvac
import sqlite3


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

class ManagedVault:
        
    def __init__(self):
        """Create Vault connection object"""
        self.client = hvac.Client(
            url=config.vault_addr,
            token=config.vault_token
        )
        self.vaults = sqlite3.connect(config.dblink)
        
    def secret_store_connected(self):
        return self.client.is_authenticated()
    
    def data_store_connected(self):
        return self.vaults.total_changes == 0
        