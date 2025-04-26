from libs import globals
from datetime import datetime
import time
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import keyring
import base64

class cryptography_class:
    def __init__(self):
        self.__server_private_key = None
        self.server_public_key = None
        self.__database_box = None

        self.client_public_key = None
        self.__client_box = None
        
        self.__fetch_server_keys()
        self.__init_database_encryption()

    def __generate_new_server_keys(self):
        print('')
        print('Generating new server key pairs.')
        print('Generating new server key pairs.')
        self.__server_private_key = PrivateKey.generate()
        self.server_public_key = self.__server_private_key.public_key
        # Encode keys as base64 strings
        private_key_str = base64.b64encode(bytes(self.__server_private_key)).decode("utf-8")
        public_key_str = base64.b64encode(bytes(self.server_public_key)).decode("utf-8")
        # Store as strings in keyring
        keyring.set_password("clockworks_server", "private_key", private_key_str)
        keyring.set_password("clockworks_server", "public_key", public_key_str)
        print('Generated new server key pairs.')

    def __fetch_server_keys(self):
        print('')
        print('Fetching server keys...')
        status = False
        while not status :
            # Try to load keys from keyring
            private_key_b64 = keyring.get_password("clockworks_server", "private_key")
            public_key_b64 = keyring.get_password("clockworks_server", "public_key")
            if private_key_b64 is None or public_key_b64 is None:
                print('Could not find server key pairs!')
                # self.__generate_new_server_keys()
                time.sleep(1)
            else:
                # Decode base64 strings
                self.__server_private_key = base64.b64decode(private_key_b64)
                self.server_public_key = base64.b64decode(public_key_b64)
                print('Server key pairs found and loaded.')
                status = True

    def init_client_encryption(self, client_public_key):
        print('')
        print('Initiating second layer encryption...')
        self.client_public_key = client_public_key
        if self.client_public_key != None :
            self.__client_box = Box(PrivateKey(self.__server_private_key), PublicKey(self.client_public_key))
            print('Second layer encryption initted.')
        else:
            print('Second layer encryption client public key not retrieved yet.')
            return False    
        
    def __init_database_encryption(self):
        print('')
        print('Initiating database encryption...')
        if self.server_public_key != None :
            self.__database_box = Box(PrivateKey(self.__server_private_key), PublicKey(self.server_public_key))
            print('Database encryption initted.')
        else:
            print('Database encryption error: key not retrieved yet.')
            return False 
            
    def get_second_layer_server_public_key(self):
        return self.server_public_key
    
    def client_encrypt_data(self, decrypted_data):
        try:
            return self.__client_box.encrypt(decrypted_data)
        except Exception as e:
            print("")
            print('Could not client encrypt data: ', e)
            return None

    def client_decrypt_data(self, encrypted_data):
        try:
            return self.__client_box.decrypt(encrypted_data)
        except Exception as e:
            print("")
            print('Could not client decrypt data: ', e)
            return None

    def database_encrypt_data(self, decrypted_data):
        try:
            return self.__database_box.encrypt(decrypted_data)
        except Exception as e:
            print("")
            print('Could not db encrypt data: ', e)
            return None

    def database_decrypt_data(self, encrypted_data):
        try:
            return self.__database_box.decrypt(encrypted_data)
        except Exception as e:
            print("")
            print('Could not db decrypt data: ', e)
            return None





