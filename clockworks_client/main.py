
from libs import globals
import os
import time                                             #Delays and debouncing
import concurrent.futures                               #Threading

# from datetime import datetime, timezone
# import numpy as np                                    #Number Arrays
# from pynput import keyboard                           #Hotkeys
# import keyboard as kby                                #Hotkeys

def main():
    list_files_in_script_directory()
    print_certificate_contents()

    threads = {} # Creating a thread dictionary to hold the executable threads and launching them
    with concurrent.futures.ThreadPoolExecutor() as executor:
        threads["remote_comms_object"] = executor.submit(globals.remote_comms_object.run)
        threads["local_comms_object"] = executor.submit(globals.local_comms_object.run)
        threads["network_check_object"] = executor.submit(globals.network_check_object.run)
        threads["fingerprint_scanner_object"] = executor.submit(globals.fingerprint_scanner_object.run)
        threads["screen_object"] = executor.submit(globals.screen_object.run)
        threads["database_object"] = executor.submit(globals.database_object.run)

        # runs forever to maintain all threads running
        while (not globals.stop_all_threads):
            time.sleep(0.1)
            for i in threads:
                # Thread closing handling
                if ((threads[i].done()) and not globals.stop_all_threads):

                    print("thread ",  i,  "stopped with error: ", threads[i].exception())
                    threads[i].cancel()
                    # Relaunch Thread
                    match i :
                        case "database_object" :
                            threads["database_object"] = executor.submit(globals.database_object.run)

                        case "remote_comms_object" :
                            threads["remote_comms_object"] = executor.submit(globals.remote_comms_object.run)

                        case "local_comms_object" :
                            threads["local_comms_object"] = executor.submit(globals.local_comms_object.run)
                        
                        case "network_check_object" :
                            threads["network_check_object"] = executor.submit(globals.network_check_object.run)
                        
                        case "fingerprint_scanner_object" :
                            threads["fingerprint_scanner_object"] = executor.submit(globals.fingerprint_scanner_object.run)
                        
                        case "screen_object" :
                            threads["screen_object"] = executor.submit(globals.screen_object.run)
                        
                        case _:
                            return "Invalid_thread"


def list_files_in_script_directory():
    # Get the absolute path of the current script
    script_path = os.path.realpath(__file__)
    
    # Get the directory name of the absolute path
    script_dir = os.path.dirname(script_path)
    
    try:
        with os.scandir(script_dir) as entries:
            print(f"Files in '{script_dir}':")
            for entry in entries:
                if entry.is_file():
                    print(entry.name)
    except FileNotFoundError:
        print(f"The directory {script_dir} does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory {script_dir}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def print_certificate_contents():
    try:
        with open(globals.remote_certificate, 'r') as cert_file:
            cert_contents = cert_file.read()
            print("Certificate Contents:\n")
            print(cert_contents)
    except FileNotFoundError:
        print(f"The file {globals.remote_certificate} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()