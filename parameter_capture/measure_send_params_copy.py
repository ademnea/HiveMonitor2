import time
import sys
import argparse
import socket
from datetime import datetime
from ssh2.session import Session
from ssh2.sftp import LIBSSH2_FXF_CREAT, LIBSSH2_FXF_WRITE, \
    LIBSSH2_SFTP_S_IRUSR, LIBSSH2_SFTP_S_IRGRP, LIBSSH2_SFTP_S_IWUSR, \
    LIBSSH2_SFTP_S_IROTH
import pexpect
import os
import csv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import Adafruit_DHT
sys.path.append('/home/pi/Desktop/HiveMonitor2/parameter_capture/hx711py')
sys.path.append('/home/pi/Desktop/HiveMonitor2/')

HIVEID =   str(3)
filename = HIVEID + ".csv" 
EMPTY_HIVE_WEIGHT = 10

##time , date and database connection setup
e = datetime.now()
date = e.strftime("%Y-%m-%d %H:%M:%S")

#set the measuring interval of parameters in minutes=---------------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\=
measuring_interval = 15
delay = measuring_interval * 60 

#initalize the pins
brood_pin = 6
honey_pin = 5
climate_pin = 21


# initializing weight module
EMULATE_HX711=False

referenceUnit = -23

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711py.hx711 import HX711
    
else:
    from hx711py.emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(2, 3)

hx.set_reading_format("MSB", "MSB")

hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

count=1


##data reading loop
while True:

    #initialize parameters to default value (2)
    weight=2
    co2 = 2
    temperature1, temperature2, temperature3 = 2, 2, 2
    humidity1, humidity2, humidity3          = 2, 2, 2

    #get the current time
    current_time = datetime.now()
    readable_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
    print()
    print("------------------------------------- RUN " + str(count) + " : (" + readable_time + ") -----------------------------------")
    print()

    ##obtaining the weight
    print("MEASURING WEIGHT")

     #incase weight sensor has issues , the default weight will be 2kg, this straight line 
     #on the weight graph will indicate an error for us 
   

    try:
        average_times=3
        weight_list=[]
        for i in range(average_times):
            val = max(0,int(hx.get_weight(5)))
            weight=(val/1000)
            weight_list.append(weight)
        averaged_weight=(sum(weight_list)/average_times)
        weight = round(averaged_weight, 0)
        hx.power_down()
        hx.power_up()
        
        
        # defaulting all invalid hiveweight values
        if weight < EMPTY_HIVE_WEIGHT:
            weight = 15
            #print("ERROR WITH WEIGHT SENSOR!.......weight = 2kg ")
            print("weight : " + str(weight) + 'kg')
        elif weight > 250:
            weight = 2
            print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")
        else:
            print("weight : " + str(weight) + 'kg')
    except:
        weight = 2
        print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")

    
    print()
    ##end of weight
        
    #obtaining temperature humidity and temperature    
    
    print("MEASURING TEMPERATURE AND HUMIDITY") #incase of any error , temp and humidity will default to 2
    print()
    try:
        humidity1, temperature1 = Adafruit_DHT.read_retry(11,5)
        
        if humidity1 is not None and temperature1 is not None:
            print ('TempHoney: {0:0.1f} C  HumidityHoney: {1:0.1f} %'.format(temperature1, humidity1))
        else:
            print("Error with honey temperature and humidity sensor")
            temperature1,  humidity1,   = 2, 2


        humidity2, temperature2 = Adafruit_DHT.read_retry(11,6)
        
        if humidity2 is not None and temperature2 is not None:
            print ('TempBrood: {0:0.1f} C  HumidityBrood: {1:0.1f} %'.format(temperature2, humidity2))
        else:
            print("Error with honey temperature and humidity sensor")
            temperature2,  humidity2,   = 2, 2
        
         
        humidity3, temperature3 = Adafruit_DHT.read_retry(11,21)
        
        if humidity3 is not None and temperature3 is not None:
            print ('TempClimate: {0:0.1f} C  HumidityClimate: {1:0.1f} %'.format(temperature3, humidity3))
        else:
            print("Error with honey temperature and humidity sensor")
            temperature3,  humidity3,   = 2, 2
        
    except:
        print("Something went completely wrong ")

            
    print()
    
    #GETTING CARBONDIOXIDE DATA
    print("MEASURING CARBONDIOXIDE") #incase of any error with sensors, temperature = 2

    # try:
    #     # with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
    #     #     i2c_connection = I2cConnection(i2c_transceiver)    
    #     #     scd41 = Scd4xI2cDevice(i2c_connection)
    #     #     scd41.set_automatic_self_calibration = True
    #     #     scd41.get_automatic_self_calibration
    #     #     

    #         # start periodic measurement in high power mode
    #         # scd41.stop_periodic_measurement()
    #         # time.sleep(1)
    #         # scd41.reinit()
    #         # time.sleep(5)
    #         # scd41.start_periodic_measurement()
        
    #     #     # Measure every 5 seconds
            
    #     # #     while True:
    #     #     for i in range(0,1):
    #     #         time.sleep(5)
    #     #         co2, temperature, humidity = scd41.read_measurement()
    #     #         print("Carbondioxide : " + "{:d} ppm CO2".format(co2.co2))
    #     #         print()

    #     #     scd41.stop_periodic_measurement()

    #     # co2 = str(co2).split(" ")[0]
    # except:
    #     co2 = "2"
    #     print("ERROR WITH CARBONDIOXIDE SENSOR....... Carbondioxide =  2")
    #     print()

        
    #WRITING TO A CSV 
    print("WRITING DATA TO CSV")
    temperature = str(temperature1) + "*" + str(temperature2) + "*" + str(temperature3)
    humidity = str(humidity1) + "*" + str(humidity2) + "*" + str(humidity3)


    carbondioxide = co2
    weight = str(weight)
    e1 = datetime.now()
    date1= e1.strftime("%Y-%m-%d %H:%M:%S")

    data = [date1 , temperature, humidity, carbondioxide, weight]
   
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    else:
        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)


    #CSV path
    csvFilepath = os.path.realpath(filename)
    print("CSV File created at : " + os.path.realpath(filename))
    print()
    #MAKE CONNECTION TO THE SERVER


    # Server details
    ssh_hostname = '137.63.185.94'
    ssh_username = 'hivemonitor'
    ssh_password = ''


    buf_size = 1024 * 1024

    host = '137.63.185.94'
    port = 22
    user = 'hivemonitor'
    password = '
    source = csvFilepath # Provide the correct CSV file path here
    destination = '/var/www/html/ademnea_website/public/arriving_hive_media/'  # Provide the correct destination path here

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        s = Session()
        s.handshake(sock)
        s.userauth_password(user, password)
        sftp = s.sftp_init()
        mode = LIBSSH2_SFTP_S_IRUSR | \
            LIBSSH2_SFTP_S_IWUSR | \
            LIBSSH2_SFTP_S_IRGRP | \
            LIBSSH2_SFTP_S_IROTH
        f_flags = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE
        fileinfo = os.stat(source)
        print("Starting copy of local file %s to remote %s:%s" % (
            source, host, destination))
        now = datetime.now()
        with open(source, 'rb') as local_fh, \
                sftp.open(destination + os.path.basename(source), f_flags, mode) as remote_fh:
            data = local_fh.read(buf_size)
            while data:
                remote_fh.write(data)
                data = local_fh.read(buf_size)
        taken = datetime.now() - now
        rate = (fileinfo.st_size / 1024000.0) / taken.total_seconds()
        print(f"Finished writing remote file in {taken}, transfer rate {rate} MB/s")
        
        # Delete the local file if the transfer was successful
        os.remove(source)
        print(f'Deleted local file: {source}')
        
    except Exception as e:
        print("An error occurred: %s" % e)


    print()
    print("Sleeping for " + str(measuring_interval) + " minutes...")
    count = count + 1
    time.sleep(delay)

   
    print()
    print()
    print()
