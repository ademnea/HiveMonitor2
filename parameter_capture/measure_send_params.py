import datetime
import sys
import os
import csv
import RPi.GPIO as GPIO
import board
import adafruit_dht
import subprocess

sys.path.append('/home/pi/Desktop/HiveMonitor2/parameter_capture/hx711py') #put to config 
sys.path.append('/home/pi/Desktop/HiveMonitor2/') #input to config 

from hx711py.hx711 import HX711
from multimedia_capture.config import node_id

HIVEID = str(node_id)
filename = "/home/pi/Desktop/HiveMonitor2/parameter_capture/sensor_data/" + HIVEID + ".csv" #put to config 
# filename = HIVEID + ".csv"
EMPTY_HIVE_WEIGHT = 10

# Set the measuring interval of parameters in minutes
measuring_interval = 15
delay = measuring_interval * 60

# Initialize DHT11 sensor objects
honey_dht11 = adafruit_dht.DHT11(board.D21)
brood_dht11 = adafruit_dht.DHT11(board.D5)
climate_dht11 = adafruit_dht.DHT11(board.D6)

# Initializing weight module
EMULATE_HX711 = False
referenceUnit = -14.975
hx = HX711(2, 3)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

def clean_and_exit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()

    print("Bye!")
    sys.exit()

def measure_weight():
    try:
        average_times = 3
        weight_list = []
        for i in range(average_times):
            val = max(0, int(hx.get_weight(5)))
            weight = val / 1000
            weight_list.append(weight)
        averaged_weight = (sum(weight_list) / average_times)
        weight = round(averaged_weight, 0)
        hx.power_down()
        hx.power_up()

        # Defaulting all invalid hive weight values
        if weight < EMPTY_HIVE_WEIGHT or weight > 250:
            weight = 2
            print("ERROR WITH WEIGHT SENSOR!.......weight = 2kg ")
    except:
        weight = 2
        print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")

    return weight

def measure_temperature_humidity(sensor):
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
    except Exception as e:
        print("Error with temperature and humidity sensor:", e)
        temperature = 2
        humidity = 2
    return temperature, humidity

def write_data_to_csv(data):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    else:
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)

# Main function
def main():
 
    current_time = datetime.datetime.now()
    readable_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
    print()
    print("------------------------------------- Date: " + readable_time + "-----------------------------------")
    print()

     # Capture multimedia files
    subprocess.run(['/bin/python', '/home/pi/Desktop/HiveMonitor2/multimedia_capture/capture.py'])

    # Measure weight
    print("MEASURING WEIGHT")
    weight = measure_weight()
    print("Weight: " + str(weight) + "kg")
    print()

    # Measure temperature and humidity
    print("MEASURING TEMPERATURE AND HUMIDITY")
    temperature_honey, humidity_honey = measure_temperature_humidity(honey_dht11)
    print("Temperature Honey: %d C" % temperature_honey + " Humidity Honey: %d %%" % humidity_honey)

    temperature_brood, humidity_brood = measure_temperature_humidity(brood_dht11)
    print("Temperature Brood: %d C" % temperature_brood + " Humidity Brood: %d %%" % humidity_brood)

    temperature_exterior, humidity_exterior = measure_temperature_humidity(climate_dht11)
    print("Temperature Exterior: %d C" % temperature_exterior + " Humidity Exterior: %d %%" % humidity_exterior)
    print()

    # Writing to a CSV
    print("WRITING DATA TO CSV")
    temperature = "{}*{}*{}".format(temperature_honey, temperature_brood, temperature_exterior)
    humidity = "{}*{}*{}".format(humidity_honey, humidity_brood, humidity_exterior)
    carbondioxide = 2  # Placeholder for CO2 measurement
    weight = str(weight)
    date1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [date1, temperature, humidity, carbondioxide, weight]
    write_data_to_csv(data)
    csv_filepath = os.path.realpath(filename)
    print("CSV File created at: " + csv_filepath)
    
    # Send all the files
    subprocess.run(['/bin/python', '/home/pi/Desktop/HiveMonitor2/multimedia_capture/send_files_to_server.py'])

    print()
    print()
    print()

# Run the main function
if __name__ == "__main__":
    main()
