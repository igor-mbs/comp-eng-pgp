
from libs import server
from libs import database
from libs import cryptography

def get_config():
    # Implement method to fetch configuration
    print('Configuration loaded.')
get_config()

stop_all_threads = False

cryptography_object = cryptography.cryptography_class()

clocking_database_file = "clocking_database_file.db"
database_object = database.database_class(clocking_database_file)

helth_check_server_path = '4cb7eb85-d2e7-4034-a276-453faa4d650b'
get_second_layer_public_key_server_path = 'fe3412b7-c51c-4ecd-a847-b036a37a8ed2'
clock_worker_server_path = 'eaaa5179-f905-4396-a740-0c14a4c2a556'
enroll_worker_server_path = 'ee2ce00e-6d12-4e5d-95a7-6a56d47e45a1'
get_client_init_data_server_path = '8f3fc897-589d-448d-8f3f-f8e49a905327'
server_domain = "0.0.0.0"
server_port = 443
server_https_public_certificate_file_name = "server_https_public_certificate.crt"
server_https_private_key_file_name = "server_https_private_key.key"
server_debug = False
server_use_reloader = False
server_object = server.server_class(
                                    helth_check_server_path                 = helth_check_server_path,
                                    get_second_layer_public_key_server_path = get_second_layer_public_key_server_path,
                                    clock_worker_server_path                = clock_worker_server_path,
                                    enroll_worker_server_path               = enroll_worker_server_path,
                                    get_client_init_data_server_path        = get_client_init_data_server_path,
                                    domain                                  = server_domain, 
                                    port                                    = server_port, 
                                    server_certificate_file_name            = server_https_public_certificate_file_name,
                                    server_key_file_name                    = server_https_private_key_file_name,
                                    debug                                   = server_debug, 
                                    use_reloader                            = server_use_reloader
                                    )