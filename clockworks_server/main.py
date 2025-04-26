from libs import globals
import os
import time                                             #Delays and debouncing
import concurrent.futures                               #Threading

def main():
    print('')
    # list_files_in_script_directory()
    print_certificate_contents()
    print('')
    
    threads = {} # Creating a thread dictionary to hold the executable threads and launching them
    with concurrent.futures.ThreadPoolExecutor() as executor:
        threads["database_object"] = executor.submit(globals.database_object.run)
        threads["server_object"] = executor.submit(globals.server_object.run)

        # runs forever to maintain all threads running
        while (not globals.stop_all_threads):
            time.sleep(0.5)
            for i in threads:
                # Thread closing handling
                if ((threads[i].done()) and not globals.stop_all_threads):

                    print("thread ",  i,  "stopped with error: ", threads[i].exception())
                    threads[i].cancel()
                    # Relaunch Thread
                    match i :
                        case "database_object" :
                            threads["database_object"] = executor.submit(globals.database_object.run)

                        case "server_object" :
                            threads["server_object"] = executor.submit(globals.server_object.run)
                        
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
        with open(globals.server_https_public_certificate_file_name, 'r') as cert_file:
            cert_contents = cert_file.read()
            print("Certificate Contents:\n")
            print(cert_contents)
    except FileNotFoundError:
        print(f"The file {globals.server_https_public_certificate_file_name} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()