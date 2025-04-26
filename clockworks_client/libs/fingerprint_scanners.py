
from libs import globals
import time
from datetime import datetime, timezone
# bastianraschke's pyfingerprint imports
from pyfingerprint.pyfingerprint import PyFingerprint
import tempfile
import hashlib
# adafruit's Adafruit-Fingerprint-Sensor-Library imports
# import board
# import busio
# from digitalio import DigitalInOut, Direction
# import adafruit_fingerprint
import json


class fingerprint_scanner :
    def __init__(self):
        self.state = 'start'
        self.worker_uuid = -1
    #
    def __del__(self):
        # self.XPVsocket.close()
        pass
    #
    def run(self):
        self.time_now = 0
        self.update_users_time = 30
        self.last_update_users_time = 0


        while (True) :
            time.sleep(0.05)
            self.time_now = time.time()
            # print('self.state: ', self.state)

            if (self.update_users_time < (self.time_now - self.last_update_users_time)) :
                print('Routinely loading templates...')
                try:
                    self.load_all_templates_from_list(globals.database_object.get_finger_print_templates_list())
                    self.last_update_users_time = self.time_now
                    print('Finished templates loading routine.')
                except:
                    print("Error templates loading routine.")

            match (self.state) :

                case 'start' :
                    while not self._start():
                        time.sleep(1)
                    self.state = 'read'

                case 'enroll' :
                    print("")
                    print("Enrolling new worker...")
                    successful_enrollment = False
                    tries = 0
                    while (successful_enrollment == False):
                        template_id, template = self._enroll()
                        if (template_id == None) or (template == None):
                            print('Could not enroll worker on fingerpirnt sensor. Trying again...')
                            successful_enrollment = False
                            tries = tries + 1
                            if tries >= 3 :
                                self.worker_name_to_be_enrolled = None
                                self.state = 'read'
                                print(f'Could not enroll worker on fingerpirnt sensor after attempting {tries} times. Aborting operation...')
                                return False
                            time.sleep(1)
                        else:
                            print('Successfully enrolled worker on fingerpirnt sensor.')
                            successful_enrollment = True
                    while not globals.remote_comms_object.enroll_worker_on_server(self.worker_name_to_be_enrolled, template_id, template) :
                        print('Could not enroll worker on server. Trying again...')
                        tries = tries + 1
                        if tries >= 3 :
                            self.worker_name_to_be_enrolled = None
                            self.state = 'read'
                            print(f'Could now enroll worker on fingerpirnt sensor after attempting {tries} times. Aborting operation...')
                            return False
                        time.sleep(5)
                    self.worker_name_to_be_enrolled = None
                    print('Successfully enrolled worker on server.')
                    self.state = 'read'

                case 'read' :
                    worker_id = self._read()
                    if ( worker_id >= 0) :
                        print('worker_id: ', worker_id)
                        globals.remote_comms_object.clock_worker(worker_id) 
                        worker_id = -1
                
                case _:
                    print('Invalid fingerprint scanner state')
                    self.state = 'read'

    def load_all_templates_from_list(self):
        pass

    def _start(self):
        pass

    def _enroll(self):
        pass

    def set_enroll_worker(self, worker_name):
        self.worker_name_to_be_enrolled = worker_name
        self.state = 'enroll'
        return True
    
    def _read(self):
        return False

    def set_read_fingerprint(self):
        self.state = 'read'
        return True
    
class dy50_class(fingerprint_scanner):
    def __init__(self):
        super().__init__()
        self.pyfp = 0
    
    def __del__(self):
        # self.XPVsocket.close()
        pass
    
    def _start(self):
        print(' ')
        print('Initializing finger print sensor...')
        try:
            # f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
            self.pyfp = PyFingerprint('/dev/ttyS2', 57600, 0xFFFFFFFF, 0x00000000)

            if ( self.pyfp.verifyPassword() == True ):
                print('Currently used templates: ' + str(self.pyfp.getTemplateCount()) +'/'+ str(self.pyfp.getStorageCapacity()))
                
                while not self.delete_all_templates() :
                    time.sleep(1)
                
                # get_all_templates_list_status = False
                # while not get_all_templates_list_status :
                #     template_list, get_all_templates_list_status = self.get_all_templates_list()
                #     time.sleep(1)
                while globals.database_object.finger_print_templates_list == None :
                    time.sleep(1)

                while not self.load_all_templates_from_list(globals.database_object.get_finger_print_templates_list()) :
                    time.sleep(1)
                
                print('Finger print sensor initialized.')
                return True
            else :
                raise Exception('The given fingerprint sensor password is wrong.')
        except Exception as e:
            print('The fingerprint sensor could not be initialized: ', e)
            return False
    
    def _enroll(self):
        print(' ')
        print('Enrolling worker...')
        try:
            print('Waiting for finger...')
            while ( self.pyfp.readImage() == False ): ## Wait that finger is read
                pass
            self.pyfp.convertImage(0x01) ## Converts read image to characteristics and stores it in charbuffer 1
            result = self.pyfp.searchTemplate() ## Checks if finger is already enrolled
            template_id = result[0]
            if ( template_id >= 0 ):
                print('Template already exists, ID: ' + str(template_id))
                raise Exception('Template already exists.')
                # return None, None        
            print('Remove finger...')
            time.sleep(2)
            print('Waiting for same finger again...')
            while ( self.pyfp.readImage() == False ): ## Wait that finger is read again
                pass
            self.pyfp.convertImage(0x02) ## Converts read image to characteristics and stores it in charbuffer 2
            if ( self.pyfp.compareCharacteristics() == 0 ): ## Compares the charbuffers
                print('Fingers do not match.')
                return None, None
            self.pyfp.createTemplate() ## Creates a template
            template_id = self.pyfp.storeTemplate() ## Saves template at new position number
            template = self.get_template_string(template_id)
            if template == None :
                return None, None
            print('Finger enrolled successfully!')
            print('New worker enrolled at ID: ' + str(template_id))
            return template_id, template
        except Exception as e:
            print('Could not enroll worker: ', e)
            return None, None
      
    def _read(self):
        # print(' ')
        # print('Reading fingerprint scanner...')
        try:
            if self.pyfp.readImage() :
                print(' ')
                print('Reading fingerprint scanner...')
                # ## Wait finger to be read
                # while ( self.pyfp.readImage() == False ):
                #     pass
                ## Converts read image to characteristics and stores it in charbuffer 1
                self.pyfp.convertImage(0x01)
                ## Searchs template
                result = self.pyfp.searchTemplate()
                positionNumber = result[0]
                accuracyScore = result[1]
                if ( positionNumber != -1 ) and (accuracyScore>=globals.fingerprint_acceptable_accuracy_score_percent) :
                    print('Template ID: ' + str(positionNumber))
                    # globals.screen_object.write_text('Worker: ' + str(globals.worker_list[positionNumber]), 3)
                    globals.screen_object.write_text('Worker: ' + str(positionNumber), 3)
                    print('Accuracy: ' + str(accuracyScore))
                    globals.screen_object.write_text('Accuracy: ' + str(accuracyScore), 4)
                    return positionNumber
                else:
                    print('No match found.')
                    globals.screen_object.write_text('No match found.', 3)
                    return -1
            return -1
        except Exception as e:
            print('Could not read finger print: ', e)
     
    def download_image(self):
        print(' ')
        print('Downloading finger print image...')
        try:
            print('Waiting for finger...')

            ## Wait that finger is read
            while ( self.pyfp.readImage() == False ):
                pass

            print('Downloading image (this take a while)...')

            imageDestination =  tempfile.gettempdir() + '/fingerprint.bmp'
            self.pyfp.downloadImage(imageDestination)

            print('The image was saved to "' + imageDestination + '".')

        except Exception as e:
            print('Could not download image.')
            print('Error: ' + str(e))

    def get_template_string(self, template_id):
        """
        Retrieves a fingerprint template by its ID and returns it as a JSON string.
        Raises an exception if the slot is empty or the operation fails.
        """
        print(' ')
        print(f'Fetching template at ID {template_id}...')
        try:
            # Load template into charbuffer 1
            if not self.pyfp.loadTemplate(template_id, 0x01):
                raise Exception(f"Template ID {template_id} could not be loaded.")
            # Download characteristics
            char_data = self.pyfp.downloadCharacteristics(0x01)
            # Convert to JSON string
            template = json.dumps(char_data)
            print("template: ")
            print(template)
            return template
        except Exception as e:
            print(f"Failed to retrieve template at ID {template_id}: {e}")
            return None

    def get_all_templates_list(self):
        """
            Downloads all fingerprint templates from the sensor and stores them
            as JSON strings in a list. Each index in the list corresponds to the
            template position in the sensor. Empty slots will contain None.
        """
        print("")
        print("Fetching all templates from fingerprint sensor...")
        status = True
        max_slots = self.pyfp.getStorageCapacity()
        template_list = [None] * max_slots  # Pre-fill with None
        # Each page contains 32 template slots
        for page in range(0, (max_slots + 31) // 32):
            try:
                index_page = self.pyfp.getTemplateIndex(page)
                for i, is_used in enumerate(index_page):
                    template_id = page * 32 + i
                    if is_used:
                        # Load template into charbuffer 1
                        self.pyfp.loadTemplate(template_id, 0x01)
                        # Download characteristics
                        char_data = self.pyfp.downloadCharacteristics(0x01)
                        # Convert to JSON string
                        json_data = json.dumps(char_data)
                        # Store in list
                        template_list[template_id] = json_data
            except Exception as e:
                print(f"Error fetching template page {page}, slot {i}: {e}")
                status = False
                continue
        print("template_list: ")
        print(template_list)
        return template_list, status

    def load_all_templates_from_list(self, template_list):
        """
        Restores fingerprint templates into the sensor at the exact indexes
        from the given list. Each index in the list corresponds to a position
        in the sensor. Items that are None are skipped.
        """
        print(" ")
        print("Loading fingerprint templates...")
        status = True
        # for template_id, json_data in enumerate(template_list):
        index = 0
        for template in template_list:
            if template is None:
                continue  # Skip empty slots
            try:
                # Convert JSON string back to list of ints
                characteristics = json.loads(template)
                # Upload to charbuffer 1
                if not (self.pyfp.uploadCharacteristics(0x01, characteristics)) :
                    print(f"Failed to upload characteristics.")
                    status = False
                print(f"Uploaded characteristics.")

                # Store in the same template ID (overwrite if necessary)
                id = self.pyfp.storeTemplate(index, 0x01)
                print(f"Restored template at ID {id} and index {index}")
            except Exception as e:
                print(f"Failed to restore template at ID {index}: {e}")
                status = False
            index = index + 1

        print("Finished loading fingerprint templates.")
        return status

    def delete_all_templates(self):
        """
        Deletes all fingerprint templates stored in the sensor.
        """
        print(' ')
        print("Deleting all fingerprint templates...")
        status = True
        max_slots = self.pyfp.getStorageCapacity()
        total_pages = (max_slots + 31) // 32
        # for page in range(0, (max_slots + 31) // 32):
        for page in range(total_pages):
            try:
                index_page = self.pyfp.getTemplateIndex(page)
                for i, is_used in enumerate(index_page):
                    template_id = page * 32 + i
                    if is_used:
                        try:
                            self.pyfp.deleteTemplate(template_id)
                            # print(f"Deleted template at ID {template_id}")
                        except Exception as e:
                            print(f"Failed to delete template {template_id}: {e}")
                            status = False
            except Exception as e:
                print(f"Failed to read page {page}: {e}")
                break  # 💡 Stop if a page is invalid — no point going further
        print("Finished deleting fingerprint templates.")
        return status















