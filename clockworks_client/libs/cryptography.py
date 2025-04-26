from libs import globals
from datetime import datetime
import time
import base64
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
# import keyring
# from keyrings.alt.file import PlaintextKeyring
# # keyring.set_keyring(EncryptedKeyring())
# keyring.set_keyring(PlaintextKeyring()) # TO DO Set up LUKS to secure the client and the keys

class cryptography_class:
    def __init__(self,
                ):
        self.second_layer_server_public_key = None
        self.second_layer_client_private_key = None
        self.second_layer_client_public_key = None
        self.box = None
        self.second_layer_client_private_key = PrivateKey.generate()    
        self.second_layer_client_public_key = self.second_layer_client_private_key.public_key

    def init_second_layer_cryptography(self):
        try:
            print('')
            print('Loading second layer encryption...')

            # # TO DO Figure out a safer solution to store the keys 
            """
            # second_layer_server_public_key_b64_encoded = keyring.get_password("clockworks_server", "second_layer_server_public_key_b64_encoded")
            # if second_layer_server_public_key_b64_encoded == None:
            #     print('')
            #     print('Could not find second layer server public key!')
            #     print('Could not find second layer server public key!')
            #     print('Could not find second layer server public key!')
            #     print('')
            #     return False
            # self.second_layer_server_public_key = PrivateKey(base64.b64decode(second_layer_server_public_key_b64_encoded))
            # second_layer_client_private_key_b64_encoded = keyring.get_password("clockworks_client", "second_layer_client_private_key_b64_encoded")
            # second_layer_client_public_key_b64_encoded = keyring.get_password("clockworks_client", "second_layer_client_public_key_b64_encoded")
            # if second_layer_client_private_key_b64_encoded is None or second_layer_client_public_key_b64_encoded is None:
            #     print('')
            #     print('Could not find second layer client key pairs, generating new ones!')
            #     print('Could not find second layer client key pairs, generating new ones!')
            #     print('Could not find second layer client key pairs, generating new ones!')
            #     print('')
            #     self.second_layer_client_private_key = PrivateKey.generate()
            #     second_layer_client_private_key_b64_encoded = base64.b64encode(bytes(self.second_layer_client_private_key)).decode("utf-8")
            #     keyring.set_password("clockworks_client", "second_layer_client_private_key_b64_encoded", second_layer_client_private_key_b64_encoded)
            #     self.second_layer_client_public_key = self.second_layer_client_private_key.public_key
            #     second_layer_client_public_key_b64_encoded = base64.b64encode(bytes(self.second_layer_client_public_key)).decode("utf-8")
            #     keyring.set_password("clockworks_client", "second_layer_client_public_key_b64_encoded", second_layer_client_public_key_b64_encoded)
            # else:
            #     print('Second layer client key pairs found and loaded.')
            #     self.second_layer_client_private_key = PrivateKey(base64.b64decode(second_layer_client_private_key_b64_encoded))
            #     self.second_layer_client_public_key = PublicKey(base64.b64decode(second_layer_client_public_key_b64_encoded))
            """

            # TO DO Find a more pratical solution than relying on connection to server to fetch public key and generating a new private key every boot
            if self.second_layer_server_public_key != None :
                # print('self.second_layer_client_private_key: ', self.second_layer_client_private_key)
                # print('self.second_layer_server_public_key: ', self.second_layer_server_public_key)
                # Box(client_private_key, server_public_key)
                # self.box = Box(PrivateKey(self.second_layer_client_private_key), PublicKey(self.second_layer_server_public_key))
                self.box = Box(self.second_layer_client_private_key, PublicKey(self.second_layer_server_public_key))
                print('Successfully loaded second layer encryption keys.')
                return True
            else:
                print('Second layer encryption server public key not retrieved yet.')
                return False    
        except Exception as e:
            print('Could not load second layer encryption: ', e)
            return False

    def get_client_public_key(self):
        return self.second_layer_client_public_key
    
    def set_second_layer_server_public_key(self, server_public_key):
        self.second_layer_server_public_key = server_public_key
        # second_layer_server_public_key_b64_encoded = base64.b64encode(bytes(self.second_layer_server_public_key)).decode("utf-8")
        # keyring.set_password("clockworks_server", "second_layer_server_public_key_b64_encoded", second_layer_server_public_key_b64_encoded)

    def encrypt_data(self, data):
        return self.box.encrypt(data)

    def decrypt_data(self, data):
        return self.box.decrypt(data)









