import socket
import os
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import uuid

# Command sending ----------------------------------------------------------------------------------
host = '10.0.0.2'
port = 9999
username = 'admin'
password = 'admin'
function_code = '2'
# 1 : Power off
# 2 : Enroll new user (Payload : Worker name)
# 3 : Restart service
# 4 : Send second layer public key
payload = 'Igor Silva'
SEND_COMMAND = False
SEND_COMMAND = True

# Second layer keys generation ---------------------------------------------------------------------
private_path="server_second_layer_private.key"
public_path="client_second_layer_public.key"
GENERATE_KEYS = False
# GENERATE_KEYS = True

# UUID generation ----------------------------------------------------------------------------------
GENERATE_UUID = False
# GENERATE_UUID = True

# Code ---------------------------------------------------------------------------------------------
def send_command(host, port, username, password, function_code, payload, SEND_COMMAND=False):
    if (SEND_COMMAND):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((host, port))
                message = f"{username},{password},{function_code},{payload}"
                client.sendall(message.encode())
                print(f"Sent: {message}")
        except Exception as e:
            print(f"Error sending TCP command: {e}")
    else:
        print('Command sending disabled.')

def generate_second_layer_keys(private_path, public_path, GENERATE_KEYS=False):
    if (GENERATE_KEYS):
        # Check if either file already exists
        if os.path.exists(private_path) or os.path.exists(public_path):
            print("Key files already exist. Operation cancelled to avoid overwriting existing keys.")
            return False

        private_key = PrivateKey.generate()
        with open(private_path, "wb") as priv_file:
            priv_file.write(bytes(private_key))
        
        public_key = private_key.public_key
        with open(public_path, "wb") as pub_file:
            pub_file.write(bytes(public_key))

        print(f"Keys successfully saved:\n - Private: {private_path}\n - Public: {public_path}")
        return True
    else:
        print('Key generating disabled.')

def generate_uuid(GENERATE_UUID=False):
    if (GENERATE_UUID):
        generated_uuid = uuid.uuid4()
        print("Generated UUID: ", generated_uuid)
    else:
        print('UUID generating disabled.')

if __name__ == "__main__":
    print('')
    send_command(host, port, username, password, function_code, payload, SEND_COMMAND)
    generate_second_layer_keys(private_path, public_path, GENERATE_KEYS)
    generate_uuid(GENERATE_UUID)
    print('')








