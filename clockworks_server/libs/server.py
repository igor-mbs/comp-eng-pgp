
from libs import globals
import time
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify
import requests
import base64
import json

# # First, generate a self-signed TLS certificate using OpenSSL:
# openssl genrsa -out server.key 2048
# openssl req -new -key server.key -out server.csr
# openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# For real HTTPS, install Certbot:
# sudo apt install certbot python3-certbot-nginx

# Get a free TLS certificate:
# sudo certbot --nginx -d yourserver.com

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

class server_class:
    def __init__(self,
                 helth_check_server_path=None,
                 get_second_layer_public_key_server_path=None,
                 clock_worker_server_path=None,
                 enroll_worker_server_path=None,
                 get_client_init_data_server_path=None,
                 domain=None, 
                 port=None, 
                 server_certificate_file_name=None,
                 server_key_file_name=None,
                 debug=None, 
                 use_reloader=None
                ):
        self.helth_check_server_path = helth_check_server_path
        self.get_second_layer_public_key_server_path = get_second_layer_public_key_server_path
        self.clock_worker_server_path = clock_worker_server_path
        self.enroll_worker_server_path = enroll_worker_server_path
        self.get_client_init_data_server_path = get_client_init_data_server_path

        
        self.domain = domain
        self.port = port

        self.server_certificate_file_name = server_certificate_file_name
        self.server_key_file_name = server_key_file_name
        self.ssl_context = (server_certificate_file_name, server_key_file_name)

        self.debug = debug
        self.use_reloader = use_reloader

        self.app = Flask(__name__)
        self._init_routes()

    def _init_routes(self):

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            # Log the error, return custom response, etc.
            # return jsonify({"error": str(e)}), 500
            print('Server encountered a request error.')
            print('Error:', e)
            return jsonify({"error": "error"}), 500

        @self.app.route(f'/{self.helth_check_server_path}', methods=['GET'])
        def helth_check():
            try:
                return jsonify({"status": "ok"}), 200
            except Exception as e:
                print("Could not check health.")
                print("Error: ", e)
                return jsonify({"error": "error"}), 400

        @self.app.route(f'/{self.get_second_layer_public_key_server_path}', methods=["POST"])
        def get_second_layer_public_key():
            print('')
            print("A client has requested the public key.")
            received_json = request.json
            client_serial_number = received_json.get('serial_number')
            # print('client_serial_number: ', client_serial_number)
            client_public_key = bytes.fromhex(received_json.get('client_second_layer_public_key'))
            # print('client_public_key: ', client_public_key)

            if (client_public_key == None) or (globals.database_object.check_serial_number_blacklist(client_serial_number)):
                return jsonify({"error": 'client public key not found'})
            globals.cryptography_object.init_client_encryption(client_public_key)
            server_public_key = globals.cryptography_object.get_second_layer_server_public_key()
            
            
            print('server_public_key: ', server_public_key)
            print('server_public_key.hex(): ', server_public_key.hex())
            
            
            return jsonify({"server_second_layer_public_key": server_public_key.hex()})

        @self.app.route(f'/{self.clock_worker_server_path}', methods=['POST'])
        def clock_worker():
            print('')
            received_json = request.json
            data = received_json.get('data')
            if (data != None):
                data = base64.b64decode(data)
                data = globals.cryptography_object.client_decrypt_data(data)
                data = json.loads(data)
                clocker_serial_number = data.get('clocker_serial_number')
                worker_id = data.get('worker_id')
                if (globals.database_object.store_clock_event(clocker_serial_number, worker_id)):
                    return jsonify({"message": "Event recorded"}), 201
            return jsonify({"error": "Missing data"}), 400

        @self.app.route(f'/{self.enroll_worker_server_path}', methods=['POST'])
        def enroll_worker():
            received_json = request.json
            data = received_json.get('data')
            if (data != None):
                data = base64.b64decode(data)
                data = globals.cryptography_object.client_decrypt_data(data)
                data = json.loads(data)
                clocker_serial_number = data.get('clocker_serial_number')
                worker_name = data.get('worker_name')
                worker_id = data.get('worker_id')
                worker_template = data.get('worker_template')
                if (globals.database_object.enroll_worker(clocker_serial_number, worker_name, worker_id, worker_template)):
                    return jsonify({"message": "Event recorded"}), 201
            return jsonify({"error": "Invalid data"}), 400

        @self.app.route(f'/{self.get_client_init_data_server_path}', methods=["POST"])
        def get_client_init_data():
            try:
                received_json = request.json
                data = received_json.get('data')
                if (data != None):
                    data = base64.b64decode(data)
                    data = globals.cryptography_object.client_decrypt_data(data)
                    data = json.loads(data)
                    finger_print_templates = globals.database_object.get_client_init_data(data.get('serial_number'))
                    finger_print_templates = [byte.decode("utf-8") for byte in finger_print_templates]
                    finger_print_templates = json.dumps(finger_print_templates)
                    finger_print_templates = finger_print_templates.encode("utf-8")
                    finger_print_templates = base64.b64encode(finger_print_templates)
                    finger_print_templates = finger_print_templates.decode("utf-8")
                    data =  {
                                "templates": finger_print_templates,
                            }
                    data = json.dumps(data)
                    data = data.encode("utf-8")
                    data = base64.b64encode(data)
                    data = globals.cryptography_object.client_encrypt_data(data)
                    data = base64.b64encode(data)
                    data = data.decode("utf-8")                    
                    return jsonify({"data": data}), 200
            except Exception as e:
                print("Error retrieving client init data:", e)
                return jsonify({"error": "Internal server error"}), 500
            
    def _check_status(self):
        try:
            print('')
            response = requests.get(f"https://127.0.0.1:{self.port}/{self.helth_check_server_path}", timeout=1, verify=False)
            # response = requests.get(f"https://127.0.0.1:{self.port}/health", timeout=1, verify=self.server_certificate_file_name)
            if(response.status_code == 200):
                print('Server is running.')
                return True
        except Exception as e:
            print(f"Server health check failed: {e}")
        return False

    def _flask_thread(self):
        # app.run(host="10.0.0.2", port=443, ssl_context=("server.crt", "server.key"))
        # app.run(host="10.0.0.1", port=443, ssl_context=("server.crt", "server.key"))
        # app.run(ssl_context=("server_cert.pem", "server_key.pem"), threaded=True)
        self.app.run(host=self.domain, port=self.port, ssl_context=self.ssl_context, debug=self.debug, use_reloader=self.use_reloader)

    def run(self):
        print("Starting server...")
        try:
            # self.app.run(host, port, debug, use_reloader)
            t = Thread(target=self._flask_thread, daemon=True)
            t.start()
            # while(self._check_status()):
            while(True):
                time.sleep(5)
        except Exception as e:
            # If an error occurs, print the error and retry
            print("Error starting server.")
            time.sleep(1)  # Wait before retrying













