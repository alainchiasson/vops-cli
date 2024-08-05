import yaml
import os

import uuid
import hvac
import sqlite3
import json


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

class AppStorage:
    """Maintinas the storage for the application

    Returns:
        _type_: _description_
    """
    
    def __init__(self):
        
        """ 
        Defines object nad creates DB file if not present.
        Will also create required teables if not already created.
        """
        
        filename = (os.path.join(os.path.dirname(__file__), config.dblink))
        self.appStorage = sqlite3.connect(filename)
        
        # Create Tables if not included. (NOTE: we will move this to a better management class later)
        db = self.appStorage
        db.execute('CREATE TABLE IF NOT EXISTS vaults (id TEXT PRIMARY KEY, url TEXT, credential TEXT, foreign key (credential) references credentials(id))')
        db.execute('CREATE TABLE IF NOT EXISTS credentials (id TEXT PRIMARY KEY, shares INTEGER, threshold INTEGER)')
    
    def data_store_connected(self):
        return self.appStorage.total_changes == 0
    
    def vault_list(self):
        """_summary_
        List Vault undermanagement
        """
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "SELECT id, url FROM vaults"
        cursor.execute(sql)
        
        vaults = cursor.fetchall()
        
        return vaults            


    def vault_add(self, name, url):
        """
        Adds a vault end point to be managed
        """
        db = self.appStorage
        cursor = db.cursor()
        sql = "INSERT INTO vaults(id, url, credential) VALUES( ?, ?, ? )"
        cursor.execute(sql, (name, url, 'NULL'))
        db.commit()
        
        return True
  
    def get_all_vaults(self):
        """_summary_
        List Vault undermanagement
        """
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "SELECT id, url, credential FROM vaults"
        cursor.execute(sql)
        
        vaults = cursor.fetchall()
        
        return vaults            


    def get_vault_by_name(self, name):
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "SELECT * FROM vaults WHERE id = ?"
        cursor.execute(sql, (name,))
        
        vault = cursor.fetchone()
        
        return vault


    def store_cred_entry(self, shares, threshold):
        
        # Hack to get a string.
        cred_id = str(uuid.uuid4())

        db = self.appStorage
        cursor = db.cursor()
        sql = "INSERT INTO credentials(id, shares, threshold ) VALUES( ?, ?, ? )"
        cursor.execute(sql, (cred_id, shares, threshold))
        db.commit()
        
        return cred_id
    
    def link_vault_to_cred(self, name, cred_id):
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "UPDATE vaults SET credential = ? WHERE id = ?"
        cursor.execute(sql, (cred_id, name))
        
        db.commit()
        
        return True

    def clear_vault_creds(self, name):
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "UPDATE vaults SET credential = 'NULL' WHERE id = ?"
        cursor.execute(sql, (name,))
        
        db.commit()
        
        return True

    def get_cred_attributes(self, cred_id):
        
        # Fetch the credentials from the DB
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "SELECT id, shares, threshold FROM credentials WHERE id = ?"
        cursor.execute(sql, (cred_id,))
        
        cred = cursor.fetchone()
        
        return cred

    def delete_unused_creds(self):
        
        db = self.appStorage
        cursor = db.cursor()
        sql = "delete from credentials where credentials.id not in (select credential from vaults)"
        cursor.execute(sql)
        db.commit()
        
        return True
        
    def remove_vault_by_name(self, name):

        db = self.appStorage
        cursor = db.cursor()
        sql = "delete FROM vaults WHERE id = ?"
        cursor.execute(sql, (name,))
        db.commit()
        
        return True
                
class ManagedVault:
        
    def __init__(self):
        """Create Vault connection object"""
        self.client = hvac.Client(
            url=config.vault_addr,
            token=config.vault_token
        )
        self.storage = AppStorage()
        self.vaults = self.storage.appStorage

        
    def show(self):
        
        """return the configuration information
        """
        
        return config
    
    def status(self):
        
        if self.storage.data_store_connected():
            return f"Verified Database storage"
        
    def verify_and_init(self):
        """ This will verify connectivty to endpoints
            validate that data is present 
            and create if it is not """
        
        return True
            
    def secret_store_connected(self):
        return self.client.is_authenticated()
    
    def data_store_connected(self):
        return self.vaults.total_changes == 0
    
    def list(self):
        """_summary_
        List Vault undermanagement
        """

        return self.storage.vault_list()
        
    def vault_add(self, name, url):
        """
        Adds a vault end point to be managed
        """
        
        return self.storage.vault_add(name, url)
    
    def vault_status(self, name):
        """_summary_
        
        Returns the status of a vault.

        Args:
            name (_type_): The NAME used to revference.
        """
       
        ( id, url, credentials ) = self.storage.get_vault_by_name(name)
        
        client = hvac.Client(
            url=url
        )
        
        if not client.sys.is_initialized():
            return "Not Initialized"
        
        if client.sys.is_sealed():
            return "Initialised but Sealed"
        
        return "Initialised and Unselaed"
    
    def vault_init(self, name):
        """Initialisze a vault system while recording the credentials.

        Args:
            name (_type_): Name of the systems to initialise.
        """
        
        ( id, url, credentials ) = self.storage.get_vault_by_name(name)
        
        client = hvac.Client(
            url=url
        )

        if client.sys.is_initialized():
            return "Already initialized - Abborting"
        
        # Initialize, store in credentials
        
        shares = 5
        threshold = 3
        result = client.sys.initialize(shares, threshold)
        
        root_token = result['root_token']
        keys = result['keys']

        unseal_keys = json.dumps(keys)
        recovery_keys = json.dumps(None)
        
        cred_id = self.storage.store_cred_entry(shares, threshold)
        
        create_response = self.client.secrets.kv.v2.create_or_update_secret(mount_point="secret", path=cred_id,
                                                                           secret=[dict(root_token=root_token),dict(unseal_keys=unseal_keys),dict( recovery_keys=recovery_keys)])

        # Update current Vault config with cred link.
        
        self.storage.link_vault_to_cred(name, cred_id)
        
        return "Initialised"
        
    def vault_unseal(self, name):
        """Unseal a vault system while recording the credentials.

        Args:
            name (_type_): Name of the systems to unseal.
        """
        
        ( id, url, credentials ) = self.storage.get_vault_by_name(name)
        
        client = hvac.Client(
            url=url
        )

        if not client.sys.is_initialized():
            return "Non Initialised, Initialise first"

        if not client.sys.is_sealed():
            return "Already Unsealed"
        
        ( cred_id, shares, threshold ) = self.storage.get_cred_attributes(credentials)
        
        secret_version_response = self.client.secrets.kv.v2.read_secret_version(
            mount_point="secret", path=credentials
        )
        
        unseal_keys = secret_version_response['data']['data']['unseal_keys']
        keys = json.loads(unseal_keys)

        # Unseal a Vault cluster with individual keys
        for key in keys[:threshold]:
            unseal_response1 = client.sys.submit_unseal_key(key)
                    
        return "Unsealed"

    def vault_remove(self, name):
        """
        Remove a vault from the configuration.
        
        """
        
        self.storage.remove_vault_by_name(name)
        
        return f"Removed config {name}"


    def prune(self):
        """
        Remove credentials in DB and Vault that are not used.
        
        """
        
        valid_creds = []
        
        vaults = self.storage.get_all_vaults()
        for vault in vaults:
   
            ( id, url, credentials ) = vault
        
            # Test if initialised.
            client = hvac.Client(
                url=url
            )

            if client.sys.is_initialized():
                valid_creds.append(credentials)
            else:
                self.storage.clear_vault_creds(id)
                
        self.storage.delete_unused_creds()
        
        list_response = self.client.secrets.kv.v2.list_secrets(
            mount_point="secret", path="/",
        )
        
        keys = list_response['data']['keys']
        
        for key in keys:
            if key not in valid_creds:
                print(f"Will delete {key}")
                
                create_response = self.client.secrets.kv.v2.delete_metadata_and_all_versions(mount_point="secret", path=key,)
                        
class Vault:
    """_summary_
    Vault class contains the defintion of the vault end point under management.
    """
    
    def __init__(self, address):
     
        self.vault_addr = address
        
    def status(self):

        self.client = hvac.Client(
            url=self.vault_addr,
        )
        
        
    
class Credential:
    """_summary_
    Credential contains the keys for the vault system being managed. This may include
     - Unseal keys, if the vault has shamir unseal
     - Recovery keys if the vault has auto unseal
     - Last used root token. The root token will be revoked after use, but stored here after generation.
    """
    
    def __init__(self, vault_init):
        
        self.root_token = vault_init.root_token
        self.recovery_keys = vault_init.recovery_keys
        self.unseal_keys = vault_init.unseal_keys

    