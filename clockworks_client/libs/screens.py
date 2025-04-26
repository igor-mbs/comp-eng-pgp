
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
import time
import math

class oled :
    def __init__(self):
        self.model = "None"
        
        self.pyfp = 0

        self.core_temperature = 0.0
        self.core_temperature_average = 0.0
        self.core_temperature_average_list_size = 50
        self.core_temperature_average_list = [0] * self.core_temperature_average_list_size
        self.core_temperature_average_index = 0

    def __del__(self):
        # self.XPVsocket.close()
        pass
    
    def run(self):
        time.sleep(1)
        pass

    def init(self):
        pass

    def get_core_temperature(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_milli = int(f.read())
                self.core_temperature = temp_milli / 100.0  # Convert to °C
                
                self.core_temperature_average_index += 1
                if (self.core_temperature_average_index >= self.core_temperature_average_list_size) :
                    self.core_temperature_average_index = 0
                self.core_temperature_average_list[self.core_temperature_average_index] = self.core_temperature
                self.core_temperature_average = sum(self.core_temperature_average_list)/len(self.core_temperature_average_list)
        except FileNotFoundError as e:
            print('Error: ', e)

    def write_text(self, text):
        pass


class oled96_class(oled) :
    def __init__(self):
        super().__init__()
        self.have_initialized = False
        self.model = "oled 0.96"
        self.device = None
        self.serial = None
        self.image = None
        self.cursor_line = 0
        self.line_height_pixels = 12
        self.display_pixel_height = 64
        self.max_line_number = math.floor(self.display_pixel_height/self.line_height_pixels)
        self.text_on_line = [" "]*self.max_line_number

    def __del__(self):
        # self.XPVsocket.close()
        pass
    
    def run(self):
        self.init()
        while(1) :
            time.sleep(2)
            if (self.have_initialized == True) :
                self.get_core_temperature()
                self.show_temperature()
                # self.draw_graph(self.core_temperature_average_list)
                self.update_display()
            else :
                self.init()

    def init(self):
        print(' ')
        print("Initializing display...")
        try:
            self.serial = i2c(port=0, address=0x3C)  # Use the correct I2C port/address
            self.device = ssd1306(self.serial)
            self.have_initialized = True
            print("Display initialized.")
        except Exception as e:
            print("Error initializing display: ", e)

    def update_display(self):
        # print(' ')
        # print('Updating display...')
        try:
            self.image = Image.new("1", self.device.size)
            draw = ImageDraw.Draw(self.image)
            font = ImageFont.load_default()
            for line_number in range(self.max_line_number) :
                line = line_number*self.line_height_pixels
                draw.text((0, line), self.text_on_line[line_number], font=font, fill=255)
            self.device.display(self.image)
            
            # Clearing old text
            for line_number in range(self.max_line_number) :
                self.text_on_line[line_number] = " "

        except Exception as e:
            print("Could not update display.")
            print("Error: ", e)

    def write_text(self, text, line_number):
        # print(' ')
        # print('Writing text on display...')
        try:
            self.text_on_line[line_number] = text
        except Exception as e:
            print("Could not write text on display.")
            print("Error: ", e)

    def draw_graph(self, var):
        print(' ')
        print('Drawing graph on display...')

        image = Image.new("1", (self.device.width, self.device.height))
        draw = ImageDraw.Draw(image)

        # Normalize temps to display height
        if var:
            min_temp = min(var)
            max_temp = max(var)
            temp_range = max(max_temp - min_temp, 1)  # Avoid divide by zero

            for i in range(1, len(var)):
                x1 = i - 1
                y1 = self.device.height - int((var[i-1] - min_temp) / temp_range * self.device.height)
                x2 = i
                y2 = self.device.width - int((var[i] - min_temp) / temp_range * self.device.width)
                draw.line((x1, y1, x2, y2), fill=255)

            # Draw current temp on top
            draw.text((0, 0), f"{var[-1]:.1f} C", fill=255)

        self.device.display(image)

    def show_temperature(self):
        self.write_text(f"CPU ºC: {self.core_temperature_average:.1f}", 0)






