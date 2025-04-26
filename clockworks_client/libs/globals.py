
import time
from libs import comms
from libs import fingerprint_scanners
from libs import screens
from libs import database
from libs import cryptography

def get_config():
    # TO DO Implement method to fetch configuration
    print('Configuration loaded.')
get_config()

stop_all_threads = False

# Production data ------------------------------------------------------------------ #
clocker_serial_number_str = '2025000001'

# Cryptography ------------------------------------------------------------------ #
cryptography_object = cryptography.cryptography_class()

# Database ------------------------------------------------------------------ #
# database_object = database.database_class()
database_object = database.ram_class()

# Fingerprint readers ------------------------------------------------------------------ #
fingerprint_acceptable_accuracy_score_percent = 90
fingerprint_scanner_object = fingerprint_scanners.dy50_class()

# Screens ------------------------------------------------------------------------------ #
screen_object = screens.oled96_class()

# Communications ----------------------------------------------------------------------- #
# remote_url = 'https://www.workclockproject.com.br'
remote_url = 'https://10.0.0.1'
helth_check_server_path = '4cb7eb85-d2e7-4034-a276-453faa4d650b'
get_second_layer_public_key_server_path = 'fe3412b7-c51c-4ecd-a847-b036a37a8ed2'
clock_worker_server_path = 'eaaa5179-f905-4396-a740-0c14a4c2a556'
enroll_worker_server_path = 'ee2ce00e-6d12-4e5d-95a7-6a56d47e45a1'
get_client_init_data_server_path = '8f3fc897-589d-448d-8f3f-f8e49a905327'
# remote_certificate = "server.crt"
# remote_certificate = "/etc/ssl/certs/server.crt"
remote_certificate = "/etc/ssl/certs/server.pem"
remote_comms_object = comms.remote_comms_class()

network_check_object = comms.network_check_class()

local_tcp_server_host = '0.0.0.0'
local_tcp_server_port = 9999
local_comms_object = comms.local_comms_class(local_tcp_server_host, local_tcp_server_port)





