
from libs import globals
import time
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import keyring
import requests
import socket
import subprocess
import os
import re
import socket
import json
import base64


class remote_comms_class :
    def __init__(self):
        self.time_last_fetch_workers_list = 0

    def __del__(self):
        # self.socket.close()
        pass
    
    def run(self):
        print('')
        print("Starting server comunicatios thread...")
        try:
            while(not globals.cryptography_object.init_second_layer_cryptography()): 
                self.get_second_layer_public_key()
                time.sleep(1)
            
            while(not self.fetch_templates_list(1)): 
                time.sleep(1)

            print("Started server comunicatios thread.")
            while (True) :    
                time.sleep(10)
                self.fetch_templates_list(30)
                # self.receive()
                # self.send()
        except Exception as e:
            print("Could not start server comunicatios thread: ", e)
            time.sleep(1)

    def get_second_layer_public_key(self):
        print('')
        print('Fetching second layer public key...')
        client_public_key = globals.cryptography_object.get_client_public_key()
        
        
        # print('client_public_key ', client_public_key)
        # print('client_public_key.encode().hex(): ', client_public_key.encode().hex())


        try:
            if client_public_key == None:
                print('Client public key not available yet.')
                return False
            payload_json =  {
                                "serial_number": globals.clocker_serial_number_str,
                                "client_second_layer_public_key": client_public_key.encode().hex(),
                            }
            server_response = requests.post(
                                            url = f"{globals.remote_url}/{globals.get_second_layer_public_key_server_path}", 
                                            json = payload_json,
                                            verify = globals.remote_certificate,
                                            timeout = 2  # seconds
                                            )
            
            
            server_public_key = server_response.json()["server_second_layer_public_key"]
            print("server_public_key: ", server_public_key)
            server_public_key = bytes.fromhex(server_response.json()["server_second_layer_public_key"])
            print("bytes.fromhex(server_public_key): ", server_public_key)
            

            globals.cryptography_object.set_second_layer_server_public_key(server_public_key)
            return True
        except Exception as e:
            print('Could not get server key: ', str(e))
            return False

    def send(self):
        pass

    def receive(self):
        decrypted_receive_message = self.box.decrypt(encrypted_receive_message)
        print("Decrypted:", decrypted_receive_message.decode())

    def clock_worker(self, worker_id):
        print('')
        print('Clocking worker...')
        payload_json =  {
                            "clocker_serial_number": globals.clocker_serial_number_str,
                            "worker_id": str(worker_id),
                        }
        plaintext_payload_json = json.dumps(payload_json).encode("utf-8")
        encrypted_payload_json = globals.cryptography_object.encrypt_data(plaintext_payload_json)
        encrypted_payload_json_b64_encoded = base64.b64encode(encrypted_payload_json).decode("utf-8")
        encrypted_payload_json =    {
                                        "data": encrypted_payload_json_b64_encoded,
                                    }
        try:
            server_response = requests.post(
                                            url = f"{globals.remote_url}/{globals.clock_worker_server_path}",
                                            json = encrypted_payload_json,
                                            verify = globals.remote_certificate,
                                            timeout = 2  # seconds
                                            )
            print("Server Response:", str(server_response.json()))
            if (server_response.status_code == 200) or (server_response.status_code == 201) :
                print("Worker clocked successfully.")
                return True
            else:
                print('Could not clock the worker.')
                return False
        except Exception as e:
            print('Could not clock the worker: ', e)
            return False 

    def fetch_templates_list(self, period):
        print('Fetching templates list...')
        time_now = time.time()
        if (time_now - self.time_last_fetch_workers_list > period) :
            self.time_last_fetch_workers_list = time_now

            payload_json =  {
                            "serial_number": globals.clocker_serial_number_str,
                            }
            plaintext_payload_json = json.dumps(payload_json).encode("utf-8")
            encrypted_payload_json = globals.cryptography_object.encrypt_data(plaintext_payload_json)
            encrypted_payload_json_b64_encoded = base64.b64encode(encrypted_payload_json).decode("utf-8")
            encrypted_payload_json =    {
                                            "data": encrypted_payload_json_b64_encoded,
                                        }
            try:
                server_response = requests.post(
                                                url = f"{globals.remote_url}/{globals.get_client_init_data_server_path}", 
                                                json = encrypted_payload_json,
                                                verify = globals.remote_certificate,
                                                timeout = 2  # seconds
                                                )
                if (server_response.status_code == 200) or (server_response.status_code == 201) :
                    print('received success fetching templates from server')
                    encrypted_data = server_response.json()["data"]
                    
                    # encrypting
                    # data = data.encode("utf-8")
                    # data = base64.b64encode(data)
                    # data = cryptography_object.encrypt_data(data)
                    # data = base64.b64encode(data)
                    # data = data.decode("utf-8")

                    # decrypting
                    # data = base64.b64decode(data)
                    # data = cryptography_object.decrypt_data(data)
                    # data = data.decode("utf-8")
                    # data = base64.b64decode(data)

                    encrypted_data = base64.b64decode(encrypted_data)
                    decrypted_data = globals.cryptography_object.decrypt_data(encrypted_data)
                    decrypted_data = decrypted_data.decode("utf-8")
                    decrypted_data = base64.b64decode(decrypted_data)
                    decrypted_data = json.loads(decrypted_data)
                    finger_print_templates = decrypted_data["templates"]
                    finger_print_templates = base64.b64decode(finger_print_templates)
                    finger_print_templates = json.loads(finger_print_templates)
                    # finger_print_templates = finger_print_templates.decode("utf-8")

                    print('Testing received templates...')
                    print('len(finger_print_templates)', len(finger_print_templates))
                    if (finger_print_templates[0] == None) and (len(finger_print_templates) == 1) :
                        print("No database for this client found on server, a new one was just created.")
                    else:
                        print("Received workers from server: ")
                    globals.database_object.update_workers_list(finger_print_templates)
                    return True
                else:
                    print("Error: ", server_response.status_code, server_response.text)
            except Exception as e:
                print('Could not fetch workers list from server: ', e)
                return False
        else:
            return False

    def enroll_worker_on_server(self, worker_name, worker_id, template):
        print('')
        print('Enrolling worker on server...')
        payload_json =  {
                            "clocker_serial_number": globals.clocker_serial_number_str,
                            "worker_name": worker_name,
                            "worker_id": str(worker_id), 
                            "worker_template": template
                        }
        plaintext_payload_json = json.dumps(payload_json).encode("utf-8")
        encrypted_payload_json = globals.cryptography_object.encrypt_data(plaintext_payload_json)
        encrypted_payload_json_b64_encoded = base64.b64encode(encrypted_payload_json).decode("utf-8")
        encrypted_payload_json =    {
                                        "data": encrypted_payload_json_b64_encoded,
                                    }
        try:
            server_response = requests.post(
                                            url = f"{globals.remote_url}/{globals.enroll_worker_server_path}",
                                            json = encrypted_payload_json,
                                            verify = globals.remote_certificate,
                                            timeout = 2  # seconds
                                            )
            print("Server Response:", str(server_response.json()))
            if (server_response.status_code == 200) or (server_response.status_code == 201) :
                print("Worker enrolled successfully.")
                return True
            else:
                print('Could not enroll worker.')
                return False
        except Exception as e:
            print('Could not enroll worker: ', e)
            return False 


class local_comms_class :
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port

    def __del__(self):
        # self.socket.close()
        pass

    def run(self):
        print('Starting TCP server...')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind((self.host, self.port))
                server.listen(5)
                print(f"TCP server started, listening on {self.host}:{self.port}")
                while True:
                    time.sleep(1)
                    try:
                        conn, addr = server.accept()
                        self.handle_client(conn, addr)
                    except Exception as e:
                        print("TCP server error:", e)
        except Exception as e:
            print("Could not start TCP server.")  
            print("Error: ", e)  
            time.sleep(1)

    def handle_client(self, conn, addr):
        try:
            print(f"New connection from {addr}.")
            data = conn.recv(1024).decode()
            parts = data.strip().split(',')
            if len(parts) == 4:
                username, password, function_code, payload = parts
                if username == "admin" and password == "admin": # TO DO Replace with hash comparrison
                    match (function_code):
                        case '1' : # Power off
                            self.power_off()
                        case '2' : # Enroll new user
                            self.enroll_new_worker(payload)
                        case '3' : # Restart service
                            self.restart_service()
                        case _:
                            print("Unknown function code")
                else:
                    print("Authentication failed")
            else:
                print("Invalid packet format")
        except Exception as e:
            print("Client handler error:", e)
        finally:
            conn.close()

    def power_off(self):
        print("Shut down command received.")
        print("Shutting down...")
        try:
            os.system("sudo poweroff")
        except Exception as e:
            print(f"Could not shut down: {e}")

    def enroll_new_worker(self, worker_name):
        print("")
        print(f"Command to enroll worker {worker_name} received.")
        globals.fingerprint_scanner_object.set_enroll_worker(worker_name)
        return True    

    def restart_service(self) :
        print("Command to restart service received.")
        print("Restarting service...")
        try:
            os.system("sudo systemctl restart workclock.service")
        except Exception as e:
            print(f"Could not restart service: {e}")


class network_check_class:
    def __init__(self):
        self.last_update_interface_info_time = 0
        # Wi-Fi
        self.wifi_ip = None
        self.wifi_ssid = None
        self.wifi_connected = None
        self.wifi_has_internet = None
        # Ethernet
        self.eth_ip = None
        self.eth_connected = None
        self.eth_has_internet = None

    def __del__(self):
        # self.socket.close()
        pass

    def run(self):
        while (True) :
            self.update_interface_info(30)
            self.display_interface_info()
            time.sleep(1)

    def get_ip_address(self, interface):
        try:
            result = subprocess.check_output(f"ip addr show {interface}", shell=True).decode()
            match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", result)
            return match.group(1) if match else None
        except Exception:
            return None

    def check_internet_access(self, interface):
        try:
            subprocess.check_output(
                f"ping -I {interface} -c 1 -W 1 8.8.8.8",
                shell=True,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_wifi_ssid(self):
        try:
            result = subprocess.check_output("iwgetid -r", shell=True).decode().strip()
            return result if result else "not connected"
        except subprocess.CalledProcessError:
            return "not connected"

    def interface_is_connected(self, interface):
        try:
            result = subprocess.check_output(f"cat /sys/class/net/{interface}/operstate", shell=True).decode().strip()
            return result == "up"
        except Exception:
            return False

    def update_interface_info(self, function_period):
        time_now = time.time()
        if ( time_now - self.last_update_interface_info_time > function_period) : 
            # Wi-Fi
            wifi_interface = "wlan0"
            self.wifi_ip = self.get_ip_address(wifi_interface)
            self.wifi_ssid = self.get_wifi_ssid()
            self.wifi_connected = self.wifi_ssid != "not connected"
            self.wifi_has_internet = self.check_internet_access(wifi_interface) if self.wifi_connected else False

            # Ethernet
            eth_interface = "end0"
            self.eth_ip = self.get_ip_address(eth_interface)
            self.eth_connected = self.interface_is_connected(eth_interface)
            self.eth_has_internet = self.check_internet_access(eth_interface) if self.eth_connected else False
            self.last_update_interface_info_time = time_now

    def display_interface_info(self):
        # print('')
        # # Wifi
        # print("Wi-Fi Interface:")
        # print(f"  IP Address: {self.wifi_ip or 'None'}")
        # print(f"  SSID: {self.wifi_ssid}")
        # print(f"  Internet Access: {'Yes' if self.wifi_has_internet else 'No'}.")
        # # Ethernet 
        # print("Ethernet Interface:")
        # print(f"  IP Address: {self.eth_ip or 'None'}")
        # print(f"  Connected: {'Yes' if self.eth_connected else 'No'}")
        # print(f"  Internet Access: {'Yes' if self.eth_has_internet else 'No'}")
        
        # globals.screen_object.write_text(f'WIFI: {self.wifi_ssid}, {self.wifi_ip or 'None'}, {'Yes' if self.wifi_has_internet else 'No'}.', 3)
        globals.screen_object.write_text(f'WIFI: {self.wifi_ip or 'None'}, {'Yes' if self.wifi_has_internet else 'No'}.', 1)
        # globals.screen_object.write_text(f'Eth: {'Yes' if self.eth_connected else 'No'}, {self.eth_ip or 'None'}, {'Yes' if self.eth_has_internet else 'No'}.', 4)
        globals.screen_object.write_text(f'Eth: {self.eth_ip or 'None'}, {'Yes' if self.eth_has_internet else 'No'}.', 2)





