from libs import globals
import sqlite3
from datetime import datetime
import time
import base64
import json



class database_class:
    def __init__(self):
        pass

    def _check_status(self):
        print('')
        print('Database is running.')
        return True # TO DO replace with a real health test
    
    def run(self):
        while(True):
            # print("Database running.")
            time.sleep(10)

    def store_clock_event(self, name):
        raise Exception("Not implemented")

    def get_worker_last_clocked_time(self, worker):
        raise Exception("Not implemented")

    def get_registered_workers(self):
        raise Exception("Not implemented")

    def update_workers_list(self, workers_list):
        raise Exception("Not implemented")


class ram_class(database_class):
    def __init__(self):
        super().__init__()
        self.finger_print_templates_list = None

    def update_workers_list(self, finger_print_templates_list):
        print('')
        print('Updating workers list...')
        self.finger_print_templates_list = finger_print_templates_list
        print('Updated workers list.')
        return True

    def get_finger_print_templates_list(self):
        # finger_print_templates_list = []
        # print('')
        # print('self.finger_print_templates_list: ', self.finger_print_templates_list)
        # print('')
        # for template in self.finger_print_templates_list :
        #     try:
        #         print('loop')
        #         print('')
        #         template = base64.b64decode(template)
        #         print('template b64decode: ', template)
        #         print('')
        #         template = globals.cryptography_object.decrypt_data(template)
        #         print('template decypt: ', template)
        #         print('')
        #         finger_print_templates_list.append(template)
        #     except Exception as e:
        #         print(f'Error processing template: {e}\n')
        # print('')
        # print('finger_print_templates_list: ', finger_print_templates_list)
        # return finger_print_templates_list
        return self.finger_print_templates_list

    
class sqlite_class(database_class):
    def __init__(self):
        super().__init__()
        self.database_file = "clockworks_database_file.db"
        with sqlite3.connect(self.database_file) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clock_events (
                    row_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    gmt_offset TEXT NOT NULL,
                    time_zone TEXT NOT NULL,
                    epoch TEXT NOT NULL
                )
            ''')

    def _check_status(self):
        print('')
        print('Database is running.')
        return True # TO DO replace with a real health test
    
    def run(self):
        print("Starting database...")
        try:
            while(self._check_status()):
                time.sleep(5)
                
        except Exception as e:
            print("Error starting database.")
            time.sleep(1)  # Wait before retrying

    def store_clock_event(self, name):
        try:

            # Get current time as a struct_time
            now = time.localtime()
            date = time.strftime("%Y-%m-%d", now)
            time_hms = time.strftime("%H:%M:%S", now)
            # Timezone offset in seconds (negative if behind UTC)
            if now.tm_isdst and time.daylight:
                offset_seconds = -time.altzone
            else:
                offset_seconds = -time.timezone
            # Convert seconds to hours
            offset_hours = offset_seconds // 3600
            gmt_offset = f"GMT{offset_hours:+d}"
            time_zone = time.strftime("%Z", now)
            epoch = time.time()

            with sqlite3.connect(self.database_file) as conn:
                conn.execute(
                    'INSERT INTO clock_events (name, date, time, gmt_offset, time_zone, epoch) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, date, time_hms, gmt_offset, time_zone, epoch)
                )
                conn.commit()
                return True
        except Exception as e:
            print('Could not store clock event on database.')
            print('Error: ', e)
            return False

    def get_worker_last_clocked_time(self, worker):
        with sqlite3.connect(self.database_file) as conn:
            cursor = conn.execute(
                '''
                SELECT timestamp 
                FROM clock_events 
                WHERE name = ?
                ORDER BY timestamp DESC 
                LIMIT 1
                ''',
                (worker,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def get_registered_workers(self):
        with sqlite3.connect(self.database_file) as conn:  # replace with self.database_file if inside a class
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM clock_events")
            rows = cursor.fetchall()
            names = [row[0] for row in rows]
        return names

    def update_workers_list(self, workers_list):
        print('')
        print('Updating workers list...')
        try:
            with sqlite3.connect(self.database_file) as conn:
                # Create table if not exists
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS workers_list (
                        row_number INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    );
                ''')
                # Insert each user (ignore if already exists)
                for name in workers_list:
                    try:
                        conn.execute('INSERT OR IGNORE INTO workers_list (name) VALUES (?)', (name,))
                    except Exception as e:
                        print(f"Could not insert user {name}: {e}")
                conn.commit()
                # print(f"Stored {len(workers_list)} users in the local database.")
                print('Updated workers list.')
                return True
        except Exception as e:
            print("Could not update workers list.")
            print('Error: ', e)




