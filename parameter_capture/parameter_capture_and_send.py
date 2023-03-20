import paramiko
import time
from Adafruit_Python_DHT  import Adafruit_DHT
import datetime 
import sys
import time
import os
import csv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice
#import analyse 

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

HIVEID = "1"
filename = HIVEID + ".csv" 

##time , date and database connection setup
e = datetime.datetime.now()
date = e.strftime("%Y-%m-%d %H:%M:%S")
#unix= time.time()
#date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

#set the measuring interval of parameters in minutes
measuring_interval = 15
delay = measuring_interval * 60 
temperature1 = 0
humidity1 = 0


## HX711 set up
# EMULATE_HX711=False

# referenceUnit = 1

# if not EMULATE_HX711:
#     import RPi.GPIO as GPIO
#     from hx711 import HX711
# else:
#     from emulated_hx711 import HX711

# def cleanAndExit():
#     print("Cleaning...")

#     if not EMULATE_HX711:
#         GPIO.cleanup()
        
#     print("Bye!")
#     sys.exit()
    
# hx = HX711(20,21)
# hx.set_reading_format("MSB", "MSB")
# hx.set_format('MSB', 'MSB')
# hx.set_reference_unit(referenceUnit)

# # hx.reset()

# hx.tare()
# ##end of HX711 set up

count = 1;

##data reading loop
while True:

    #get the current time
    current_time = datetime.datetime.now()
    readable_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
    print()
    print("------------------------------------- RUN " + str(count) + " : (" + readable_time + ") -----------------------------------")
    print()

    ##obtaining the weight
    print("MEASURING WEIGHT")

    try: #incase weight sensor has issues , the default weight will be 2kg, this straight line 
         #on the weight graph will indicate an error for us 
        # hx.reset()
        # time.sleep(5)
        # hx.tare()
        # time.sleep(5)
        # sum_weight =  0
        # for i in range(5): #Setting a mean value for the weight we shall have read 
        #     sample_weight = 0
        #     sample_weight = hx.get_weight(7)
        #     sum_weight= sum_weight + sample_weight
        
        # weight = round(sum_weight/5, 2)##converting the weight to kgs
        
        #defaulting all temperature values below 40kgs to 40kgs
        if weight < 40:
            weight = 2
            print("ERROR WITH WEIGHT SENSOR!.......weight = 2kg ")
        elif weight > 250:
            weight = 2
            print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")
        else:
            print("weight : " + str(weight) + 'kg')
    except:
        weight = 2
        print("ERROR WITH WEIGHT SENSOR! .......weight = 2kg ")

    
    print()
#     hx.power_down()## put the hx711 to sleep


    ##end of weight
        
    #obtaining temperature humidity and temperature    
    
    print("MEASURING TEMPERATURE AND HUMIDITY") #incase of any error , temp and humidity will default to 2

    print()

    try:
        humidity1, temperature1 = Adafruit_DHT.read_retry(11,4)
    except:
        print("Error with honey temperature and humidity sensor")
        temperature1,  humidity1,   = 2, 2
    print ('TempHoney: {0:0.1f} C  HumidityHoney: {1:0.1f} %'.format(temperature1, humidity1))

    try:
        humidity2, temperature2 = Adafruit_DHT.read_retry(11,6)
    except:
        print("Error with brood temperature and humidity sensor")
        temperature2,  humidity2,   = 2, 2
    print ('TempBrood: {0:0.1f} C  HumidityBrood: {1:0.1f} %'.format(temperature2, humidity2))
         
    try: 
        humidity3, temperature3 = Adafruit_DHT.read_retry(11,12)
    except:
        print("Error with climate temperature and humidity sensor ")
        temperature3,  humidity3,   = 2, 2
    print ('TempClimate: {0:0.1f} C  HumidityClimate: {1:0.1f} %'.format(temperature3, humidity3))

            
    print()
  
    
    #GETTING CARBONDIOXIDE DATA
    print("MEASURING CARBONDIOXIDE") #incase of any error with sensors, temperature = 2
    co2 = 0

    try:
        with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
            i2c_connection = I2cConnection(i2c_transceiver)    
            scd41 = Scd4xI2cDevice(i2c_connection)
        #     scd41.set_automatic_self_calibration = True
        #     scd41.get_automatic_self_calibration
        #     

            # start periodic measurement in high power mode
            scd41.stop_periodic_measurement()
            time.sleep(1)
            scd41.reinit()
            time.sleep(5)
            scd41.start_periodic_measurement()
        
            # Measure every 5 seconds
            
        #     while True:
            for i in range(0,1):
                time.sleep(5)
                co2, temperature, humidity = scd41.read_measurement()
                print("Carbondioxide : " + "{:d} ppm CO2".format(co2.co2))
                print()

            scd41.stop_periodic_measurement()

        co2 = str(co2).split(" ")[0]
    except:
        co2 = "2"
        print("ERROR WITH CARBONDIOXIDE SENSOR....... Carbondioxide =  2")

        
    #WRITING TO A CSV 
    print("WRITING DATA TO CSV")
    temperature = str(temperature1) + "*" + str(temperature2) + "*" + str(temperature3)
    humidity = str(humidity1) + "*" + str(humidity2) + "*" + str(humidity3)
    
   

    
    carbondioxide = co2
    weight = str(weight)
    e1 = datetime.datetime.now()
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
    print("ESTABLISHING CONNECTION TO THE SERVER")
    try:
        ssh.connect('137.63.185.94',username='hivemonitor', password= 'Ad@mnea321')
        print("Connected successfully")
        sftp = ssh.open_sftp()
    except:
        print("Establishing connection to the server failed, will try again later...")

    print()
    
    ##sending the data  to the server
    print("SENDING CSV TO SERVER")
    try:
        sftp.put( csvFilepath,"/var/www/html/ademnea_website/public/arriving_hive_media/"+filename)
        time.sleep(5)
        os.remove(filename)
        print("Status : Sent successfully")
    except:
        print("Status : Encountered issues while sending csv , will try again later")

    try:
        ssh.close()
        print()
        print("SSH client closed successfully")
    except:
        print("Failed to close connection")

    print()
    print("Sleeping for " + str(measuring_interval) + " minutes...")
    time.sleep(delay)

    count = count + 1
    print()
    print()
    print()
#     