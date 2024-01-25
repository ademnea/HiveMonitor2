import os
import sys
import csv
import time
import smbus
import board
import datetime
import subprocess
import numpy as np
import adafruit_dht
import RPi.GPIO as GPIO
from scipy import fftpack
from sensirion_i2c_scd import Scd4xI2cDevice
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection

# select the correct i2c bus for this revision of Raspberry Pi
revision = ([l[12:-1] for l in open('/proc/cpuinfo','r').readlines() if l[:8]=="Revision"]+['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

# ADXL345 constants
EARTH_GRAVITY_MS2   = 9.80665
SCALE_MULTIPLIER    = 0.004

DATA_FORMAT         = 0x31 # This is used to set the sensitivity to 16g by accessing the register
BW_RATE             = 0x2C
POWER_CTL           = 0x2D

BW_RATE_1600HZ      = 0x0F # used for the bandwidth setting
BW_RATE_800HZ       = 0x0E
BW_RATE_400HZ       = 0x0D
BW_RATE_200HZ       = 0x0C
BW_RATE_100HZ       = 0x0B
BW_RATE_50HZ        = 0x0A
BW_RATE_25HZ        = 0x09

RANGE_2G            = 0x00
RANGE_4G            = 0x01
RANGE_8G            = 0x02
RANGE_16G           = 0x03

MEASURE             = 0x08
AXES_DATA           = 0x32

#other constants
samples_to_read = 10000
sample_rate = 1030

channel_1 = []
channel_2 = []
channel_3 = []


sys.path.append('/home/pi/Desktop/HiveMonitor2/') #TODO: input to config 
sys.path.append('/home/pi/Desktop/HiveMonitor2/parameter_capture/hx711py') #TODO: input to config 

from hx711py.hx711 import HX711
from multimedia_capture.config import node_id


class ParameterCapture:

    # Initialize the class with necessary configurations
    def __init__(self):
        self.HIVEID = str(node_id)
        self.filename = f"/home/pi/Desktop/HiveMonitor2/parameter_capture/sensor_data/{self.HIVEID}.csv"
        self.EMPTY_HIVE_WEIGHT = 10

        # Initialize DHT11 sensors
        self.honey_dht11 = adafruit_dht.DHT11(board.D21)
        self.brood_dht11 = adafruit_dht.DHT11(board.D5)
        self.climate_dht11 = adafruit_dht.DHT11(board.D6)

        # Initialize weight module
        self.EMULATE_HX711 = False
        self.referenceUnit = -52.14
        self.hx = HX711(0, 1)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.referenceUnit)
        self.hx.reset()
        self.hx.tare() 
       

    # Clean up and exit the program
    def clean_and_exit(self):
        print("Cleaning...")
        GPIO.cleanup()
        print("Bye!")
        sys.exit()

    # Measure hive weight using the weight module
    def measure_weight(self):
        try:
            average_times = 3
            weight_list = []
            for i in range(average_times):
                val = max(0, int(self.hx.get_weight(5)))
                weight = val / 1000
                weight_list.append(weight)
            averaged_weight = (sum(weight_list) / average_times)
            weight = round(averaged_weight, 0)
            self.hx.power_down()
            self.hx.power_up()

            if weight < self.EMPTY_HIVE_WEIGHT or weight > 250:
                weight = 2
                print("ERROR WITH WEIGHT SENSOR!.......weight = 2kg ")
        except:
            weight = 2
            print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")

        return weight

    # Measure temperature and humidity using DHT11 sensor
    def measure_temperature_humidity(self, sensor):
        try:
            temperature = sensor.temperature
            humidity = sensor.humidity
        except Exception as e:
            print("Error with temperature and humidity sensor:", e)
            temperature = 2
            humidity = 2
        return temperature, humidity

    def capture_carbondioxide(self):
        try:
            with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
                i2c_connection = I2cConnection(i2c_transceiver)    
                scd41 = Scd4xI2cDevice(i2c_connection)
                scd41.set_automatic_self_calibration = True
                scd41.get_automatic_self_calibration

                # Start periodic measurement in high power mode
                scd41.stop_periodic_measurement()
                time.sleep(1)
                scd41.reinit()
                time.sleep(5)
                scd41.start_periodic_measurement()

                # Measure every 5 seconds
                for i in range(0, 1):
                    time.sleep(5)
                    co2, temperature, humidity = scd41.read_measurement()
                    print("Carbondioxide : " + "{:d} ppm CO2".format(co2.co2))

                scd41.stop_periodic_measurement()

            co2 = str(co2).split(" ")[0]
        except:
            co2 = "2"
            print("ERROR WITH CARBONDIOXIDE SENSOR....... Carbondioxide =  2")
            print()

        return co2

    #####functions#####
    def conv_str_tag(channel, tag):
        # Convert every channel from int to str, separated by a coma and adds tags at the beginning and end.
        n = len(channel)
        s_channel = '<' + tag + '>'
        for i in range(n-1):
            s_channel = s_channel + str(channel[i]) + ','
        s_channel = s_channel + str(channel[n-1]) + '</'+ tag + '>'
        return s_channel

    #####Add tags and save on file#####
    def record(channel_1, channel_2, channel_3, archive):
        str_channel = ''
        str_channel += conv_str_tag(channel_1, 'L1') + '\n'
        str_channel += conv_str_tag(channel_2, 'L2') + '\n'
        str_channel += conv_str_tag(channel_3, 'L3') + '\n'

        # Write to file
        arch = open("/home/pi/Desktop/HiveMonitor2/VIBRATIONSENSOR/textfile/"+archive, "w")
        arch.write(str_channel)
        arch.close()

    # Write data to CSV file
    def write_data_to_csv(self, data):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        else:
            with open(self.filename, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(data)

    # Run the data capture process
    def run_capture(self):
        current_time = datetime.datetime.now()
        readable_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
        print("\n")
        print("------------------------------------- Date:", readable_time, "-----------------------------------")
        print()

        # Capture multimedia files
        subprocess.run(['/bin/python', '/home/pi/Desktop/HiveMonitor2/multimedia_capture/capture.py'])

        # Capture carbon dioxide levels
        co2 = self.capture_carbondioxide()
        print("Carbondioxide:", co2, "ppm")
        print()

        # Measure hive weight
        weight = self.measure_weight()
        print("Weight:", weight, "kg")
        print()

        # Measure temperature and humidity for different sections
        temperature_honey, humidity_honey = self.measure_temperature_humidity(self.honey_dht11)
        temperature_brood, humidity_brood = self.measure_temperature_humidity(self.brood_dht11)
        temperature_exterior, humidity_exterior = self.measure_temperature_humidity(self.climate_dht11)
        print("Temperature Honey:", temperature_honey, "C Humidity Honey:", humidity_honey, "%")
        print("Temperature Brood:", temperature_brood, "C Humidity Brood:", humidity_brood, "%")
        print("Temperature Exterior:", temperature_exterior, "C Humidity Exterior:", humidity_exterior, "%")
        print()

        # Write data to CSV
        print("WRITING DATA TO CSV")
        temperature = "{}*{}*{}".format(temperature_honey, temperature_brood, temperature_exterior)
        humidity = "{}*{}*{}".format(humidity_honey, humidity_brood, humidity_exterior)
        carbondioxide = co2
        weight = str(weight)
        date1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [date1, temperature, humidity, carbondioxide, weight]
        self.write_data_to_csv(data)
        csv_filepath = os.path.realpath(self.filename)
        print("CSV File created at:", csv_filepath)


        # Send captured files to server
        subprocess.run(['/bin/python', '/home/pi/Desktop/HiveMonitor2/multimedia_capture/send_files_to_server.py'])

        print("\n\n")

# Create an instance of ParameterCapture class and run the capture process
if __name__ == "__main__":
    capture = ParameterCapture()

    # while(True):
    capture.run_capture()
        # time.sleep(1)
