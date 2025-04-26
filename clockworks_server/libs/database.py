from libs import globals
import sqlite3
from datetime import datetime
import time
import base64
import os

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

class database_class:
    def __init__(self,
                 clockworks_server_database_file = "clockworks_server_database.db"
                ):
        self.clockworks_server_database_file = clockworks_server_database_file
        self._init_clocking_database()

    def _init_clocking_database(self):
        print('')
        print('Checking database status...')
        if os.path.exists(self.clockworks_server_database_file):
            print("Database exists.")
        else:
            print('')
            print("Database not found! Creating new database...")
            print("Database not found! Creating new database...")
            print("Database not found! Creating new database...")
            print('')
            with sqlite3.connect(self.clockworks_server_database_file) as conn:
                pass  # Just opening the connection creates the file
            print("Database created successfully.")

    def _check_status(self):
        print('')
        print('Database is running.')
        return True
    
    def run(self):
        print("Starting database...")
        try:
            # while(self._check_status()):
            while(True):
                time.sleep(5)
        except Exception as e:
            print("Error starting database.")
            time.sleep(1)  # Wait before retrying

    def check_if_table_exists(self, cursor, table_name):
        cursor.execute(f'''
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name=?
                        ''', (table_name,))
        return cursor.fetchone() is not None
        
    def store_clock_event(self, clocker_serial_number, received_worker_id):
        print('')
        print('Storing clock event...')
        try:
            db_worker_id = int(received_worker_id) + 1
            # Get current time as a struct_time
            now = time.localtime()
            # date = time.strftime("%Y-%m-%d", now)
            # time_hms = time.strftime("%H:%M:%S", now)
            # Timezone offset in seconds (negative if behind UTC)
            if now.tm_isdst and time.daylight:
                offset_seconds = -time.altzone
            else:
                offset_seconds = -time.timezone
            offset_hours = offset_seconds // 3600 # Convert seconds to hours
            gmt_offset = f"GMT{offset_hours:+d}"
            # time_zone = time.strftime("%Z", now)
            epoch = time.time()

            serial_number_clocking_table = clocker_serial_number + "_clocking_table"

            with sqlite3.connect(self.clockworks_server_database_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (serial_number_clocking_table,))
                if cursor.fetchone() is None:
                    print(f"Error clocking worker: Table '{serial_number_clocking_table}' does not exist.")
                    return False
                else:
                    cursor.execute(f'PRAGMA table_info("{serial_number_clocking_table}")')
                    columns = [column[1] for column in cursor.fetchall()]
                    print(f'columns: {columns}')
                    print(f'columns[db_worker_id = {db_worker_id}]: {columns[db_worker_id]}')
                    cursor.execute(f'''
                                        INSERT INTO "{serial_number_clocking_table}" ("{columns[db_worker_id]}")
                                        VALUES (?)
                                    ''', (epoch,))
                    conn.commit()
                    print(f'Clocked worker on database.')
                    return True
                    # for column in columns:
                        # if globals.cryptography_object.client_decrypt_data(column) == received_worker_name :
                            # cursor.execute(f'''
                            #                     INSERT INTO {serial_number_clocking_table} ({column})
                            #                     VALUES (?)
                            #                 ''', (epoch,))
                            # conn.commit()
                            # return True
                    # print("Could not clock worker: Worker not found in table.")
                    # return False
        except Exception as e:
            print('Could not store clock event on database: ', e)
            return False

    def get_client_init_data(self, clocker_serial_number):
        print('')
        print('Getting client init data...')
        try:
            with sqlite3.connect(self.clockworks_server_database_file) as conn:
                cursor = conn.cursor()

                serial_number_fingerprint_template_table = clocker_serial_number + "_fingerprint_template_table"
                table_exists = self.check_if_table_exists(cursor, serial_number_fingerprint_template_table)
                if not table_exists:
                    print(f"Table {serial_number_fingerprint_template_table} does not exist, creating...")
                    cursor.execute(f'''
                                        CREATE TABLE IF NOT EXISTS "{serial_number_fingerprint_template_table}" (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT
                                            -- Add worker name columns dynamically later as needed
                                        )
                                    ''')
                    print(f'Table "{serial_number_fingerprint_template_table}" created.')
                else:
                    print(f'Table "{serial_number_fingerprint_template_table}" exists.')

                cursor.execute(f'PRAGMA table_info("{serial_number_fingerprint_template_table}")')
                worker_names = [column[1] for column in cursor.fetchall()]
                finger_print_templates = []
                print('')
                print('worker_names: ', worker_names)
                print('')
                for worker in worker_names:
                    if worker == "id":
                        print('continue')
                        continue  # Skip ID column
                    else:
                        cursor.execute(f'SELECT "{worker}" FROM "{serial_number_fingerprint_template_table}" ORDER BY "id" DESC LIMIT 1')
                        most_recent_row = cursor.fetchone()
                        if most_recent_row:
                            print(f'at {worker} append(most_recent_row[0])')
                            finger_print_templates.append(most_recent_row[0])
                        else:
                            print(f'at {worker} append(None)')
                            finger_print_templates.append(None)
        
                if len(finger_print_templates) > 0 :
                    index = 0
                    for template in finger_print_templates:
                            template = base64.b64decode(template)
                            template = globals.cryptography_object.database_decrypt_data(template)
                            template = template.decode("utf-8")
                            template = base64.b64decode(template)
                            finger_print_templates[index] = template
                            index = index + 1
                else:
                    print('finger_print_templates is empty, appending None.')
                    finger_print_templates.append(None)
                print('Getting client init data success.')
                return finger_print_templates
        except Exception as e:
            print('Could not get client init data: ', e)

    def enroll_worker(self, clocker_serial_number, received_worker_name, worker_id, received_worker_template):
        print('')
        print('Enrolling new worker...')
        try:
            serial_number_clocking_table = clocker_serial_number + "_clocking_table"
            serial_number_fingerprint_template_table = clocker_serial_number+"_fingerprint_template_table"

            received_worker_name = base64.b64encode(received_worker_name.encode("utf-8"))
            encrypted_received_worker_name = globals.cryptography_object.database_encrypt_data(received_worker_name)
            encrypted_received_worker_name = base64.b64encode(encrypted_received_worker_name).decode("utf-8")

            worker_id = int(worker_id)
            database_worker_id = worker_id+2 # Added 1 because the table starts with the "id" columns and added 1 more because the database starts counting on 1 not 0
            
            print('')
            print('received_worker_template: ', received_worker_template)
            print('')
            received_worker_template = received_worker_template.encode("utf-8")
            print('received_worker_template.encode("utf-8"): ', received_worker_template)
            print('')
            received_worker_template = base64.b64encode(received_worker_template)
            print('base64.b64encode(received_worker_template): ', received_worker_template)
            print('')
            encrypted_received_worker_template = globals.cryptography_object.database_encrypt_data(received_worker_template)
            encrypted_received_worker_template = base64.b64encode(encrypted_received_worker_template).decode("utf-8")
            
            with sqlite3.connect(self.clockworks_server_database_file) as conn:
                cursor = conn.cursor()
                
                def create_table(cursor, table_name):
                        try:
                            cursor.execute(f'''
                                                CREATE TABLE IF NOT EXISTS "{table_name}" (
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT
                                                )
                                            ''')
                            print(f"Created table '{serial_number_clocking_table}'.")
                            return True
                        except:
                            return False
                
                if not (self.check_if_table_exists(cursor, serial_number_clocking_table)) :
                    if not (create_table(cursor, serial_number_clocking_table)) :
                        print(f'Error creating database "{serial_number_clocking_table}".')
                        return False
                
                if not (self.check_if_table_exists(cursor, serial_number_fingerprint_template_table)) :
                    if not (create_table(cursor, serial_number_fingerprint_template_table)) :
                        print(f'Error creating database "{serial_number_fingerprint_template_table}".')
                        return False
                    
                def update_table(cursor, table_name) :
                    try:
                        cursor.execute(f'PRAGMA table_info("{table_name}")')
                        columns = cursor.fetchall()
                        if (database_worker_id <= 1) : # Forbidden value
                            print("Error, worker id is lesser than 0, forbidden value.")
                            return False
                        elif (1 < database_worker_id < len(columns)) : # 1 < 2 < 3 # Rewriting some user
                            print("Error, trying to rewrite user.")
                            return False
                            # print(f'Worker ID "{worker_id}" exists in database "{table_name}".')
                            # db_encrypted_worker_name = columns[worker_id][1]
                            # cursor.execute(f'''
                            #                     ALTER TABLE "{table_name}" RENAME COLUMN "{db_encrypted_worker_name}" TO "{encrypted_received_worker_name}"
                            #                 ''')
                            # print(f'Renamed column "{db_encrypted_worker_name}" to "{encrypted_received_worker_name}" at table "{table_name}".')
                        elif (database_worker_id == (len(columns)+1)) : # 3 == 4 # Write new user
                            print(f'Worker ID "{worker_id}" does not exist in database "{table_name}, max is "{(len(columns)-2)}".')
                            cursor.execute(f'''
                                                ALTER TABLE "{table_name}" ADD COLUMN "{encrypted_received_worker_name}" TEXT NOT NULL DEFAULT ''
                                            ''')
                            print(f'Added worker ID {worker_id} at the end of table "{table_name}".')
                            if table_name == serial_number_fingerprint_template_table:
                                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                                row_count = cursor.fetchone()[0]
                                if row_count == 0:
                                    cursor.execute(f'INSERT INTO "{table_name}" DEFAULT VALUES')
                                cursor.execute(f'''
                                                    UPDATE "{table_name}"
                                                    SET "{encrypted_received_worker_name}" = ?
                                                    WHERE rowid = 1
                                                ''', (encrypted_received_worker_template,))
                                print(f'Inserted template in row 1, column "{database_worker_id}" of the table "{table_name}".')
                            return True
                        elif (len(columns) < database_worker_id) : # 3 < 4 # Write new user skipping columns
                            print("Error, trying to write user skipping columns.")
                            return False
                            # print(f'Worker ID "{worker_id}" does not exist in database "{table_name}, max is "{(len(columns)-1)}".')
                            # for index in range(len(columns),  database_worker_id) : 
                            #     if index == len(columns) :
                            #         continue
                            #     else:
                            #         if index == database_worker_id : 
                            #             cursor.execute(f'''
                            #                                 ALTER TABLE "{table_name}" ADD COLUMN "{encrypted_received_worker_name}" TEXT NOT NULL DEFAULT ''
                            #                             ''')
                            #             print(f'Added worker ID {decrypted_worker_id} at the end of table "{table_name}".')
                            #             if table_name == serial_number_fingerprint_template_table:
                            #                 cursor.execute(f'''
                            #                                     UPDATE "{table_name}"
                            #                                     SET "{encrypted_received_worker_name}" = ?
                            #                                     WHERE rowid = 1
                            #                                 ''', (encrypted_received_worker_template,))
                            #                 print(f'Inserted template in row 1, column "{index}" of the table "{table_name}".')
                            #         else:
                            #             cursor.execute(f'''
                            #                                 ALTER TABLE "{table_name}" ADD COLUMN "{None}" TEXT DEFAULT ''
                            #                             ''')
                            #             print(f'Added filler column "None" at index "{index}" in table "{table_name}".')
                        else: # Unidentified error
                            print("Unidentified error enrolling user in database.")
                            return False
                    except:
                        return False
                status3 = update_table(cursor, serial_number_clocking_table)
                status4 = update_table(cursor, serial_number_fingerprint_template_table)
                conn.commit()

                if status3 and status4 :
                    print('Successfully enrolled user in database.')
                    return True
                else:
                    print(f'Failed Enrolling user in database: 3={status3}, 4={status4}.')
                    return False
        except Exception as e:
            print('Could not enroll worker: ', e)
            return False

    def check_serial_number_blacklist(self, serial_number):
        return False # TO DO create a database of blacklisted clients for theft cases and alike
















