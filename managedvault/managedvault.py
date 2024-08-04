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

class ManagedVault:
        
    def __init__(self):
        """Create Vault connection object"""
        self.client = hvac.Client(
            url=config.vault_addr,
            token=config.vault_token
        )
        self.vaults = sqlite3.connect((os.path.join(os.path.dirname(__file__), config.dblink)))
        
    def verify_and_init(self):
        """ This will verify connectivty to endpoints
            validate that data is present 
            and create if it is not """
        
        db = self.vaults
        db.execute('CREATE TABLE IF NOT EXISTS vaults (id TEXT PRIMARY KEY, url TEXT, credential TEXT, foreign key (credential) references credentials(id))')
        db.execute('CREATE TABLE IF NOT EXISTS credentials (id TEXT PRIMARY KEY, shares INTEGER, threshold INTEGER)')
        db.close()
        return True
            
    def secret_store_connected(self):
        return self.client.is_authenticated()
    
    def data_store_connected(self):
        return self.vaults.total_changes == 0
    
    def list_vaults(self):
        """_summary_
        List Vault undermanagement
        """
        
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT id, url FROM vaults"
        cursor.execute(sql)
        print(cursor.fetchall())

    def vault_add(self, name, url):
        """
        Adds a vault end point to be managed
        """
        db = self.vaults
        cursor = db.cursor()
        sql = "INSERT INTO vaults(id, url, credential) VALUES( ?, ?, ? )"
        cursor.execute(sql, (name, url, 'NULL'))
        db.commit()
    
    def vault_status(self, name):
        """_summary_
        
        Returns the status of a vault.

        Args:
            name (_type_): The NAME used to revference.
        """
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT * FROM vaults WHERE id = ?"
        cursor.execute(sql, (name,))
        
        ( id, url, credentials ) = cursor.fetchone()
        
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
        
        # Get Vault URL
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT * FROM vaults WHERE id = ?"
        cursor.execute(sql, (name,))
        
        ( id, url, credentials ) = cursor.fetchone()
        
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
        
        # Hack to get a string.
        cred_id = str(uuid.uuid4())
        
        db = self.vaults
        cursor = db.cursor()
        sql = "INSERT INTO credentials(id, shares, threshold ) VALUES( ?, ?, ? )"
        cursor.execute(sql, (cred_id, shares, threshold))
        db.commit()

        svault = self.client
                            
        create_response = svault.secrets.kv.v2.create_or_update_secret(mount_point="secret", path=cred_id,
                                                                           secret=[dict(root_token=root_token),dict(unseal_keys=unseal_keys),dict( recovery_keys=recovery_keys)])
                

        # Update current Vault config with cred link.
        
        db = self.vaults
        cursor = db.cursor()
        sql = "UPDATE vaults SET credential = ? WHERE id = ?"
        cursor.execute(sql, (cred_id, name))
        
        db.commit()
        
        return "Initialised"
        
    def vault_unseal(self, name):
        """Unseal a vault system while recording the credentials.

        Args:
            name (_type_): Name of the systems to unseal.
        """
        
        # Get Vault URL
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT * FROM vaults WHERE id = ?"
        cursor.execute(sql, (name,))
        
        ( id, url, credentials ) = cursor.fetchone()
        
        client = hvac.Client(
            url=url
        )

        if not client.sys.is_initialized():
            return "Non Initialised, Initialise first"

        if not client.sys.is_sealed():
            return "Already Unsealed"
        
        # Fetch the credentials from the DB
        
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT id, shares, threshold FROM credentials WHERE id = ?"
        # sql = "SELECT id, shares, threshold, root_token, unseal_keys, recovery_keys FROM credentials WHERE id = ?"
        cursor.execute(sql, (credentials,))
        
        ( cred_id, shares, threshold ) = cursor.fetchone()
        # ( cred_id, shares, threshold, root_token, unseal_keys, recovery_keys ) = cursor.fetchone()

        svault = self.client
        
        secret_version_response = svault.secrets.kv.v2.read_secret_version(
            mount_point="secret", path=credentials
        )
        
        unseal_keys = secret_version_response['data']['data']['unseal_keys']
                                
        keys = json.loads(unseal_keys)

        # Unseal a Vault cluster with individual keys
        for key in keys[:threshold]:
            unseal_response1 = client.sys.submit_unseal_key(key)
                    
        return "Unsealed"
        
    def vault_credentials(self):
        """
        Take credentials from the DB and place in vault.
        
        """
        svault = self.client
        
        # Get all credentials vaules.
        db = self.vaults
        cursor = db.cursor()
        sql = "SELECT id, root_token, unseal_keys, recovery_keys FROM credentials"
        cursor.execute(sql)
            
        for cred_row in cursor.fetchall():
            (id, root_token, unseal_keys, recovery_keys) = cred_row
                            
            create_response = svault.secrets.kv.v2.create_or_update_secret(mount_point="secret", path=id,
                                                                           secret=[dict(root_token=root_token),dict(unseal_keys=unseal_keys),dict( recovery_keys=recovery_keys)])
                
        return "Keys Vaulted"           
        
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

    