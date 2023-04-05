import paramiko
import time
import datetime
import time
import os
import csv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import board
import adafruit_dht


from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice
#import analyse 

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

HIVEID = "2"
filename = HIVEID + ".csv" 

##time , date and database connection setup
e = datetime.datetime.now()
date = e.strftime("%Y-%m-%d %H:%M:%S")

#set the measuring interval of parameters in minutes
measuring_interval = 15
delay = measuring_interval * 60 


# Initialize DHT11 sensor objects
honey_dht11 = adafruit_dht.DHT11(board.D4)
brood_dht11 = adafruit_dht.DHT11(board.D5)
climate_dht11 = adafruit_dht.DHT11(board.D6)

#initialize temperature and humidity to default
temperature1, temperature2, temperature3 = 2, 2, 2
humidity1, humidity2, humidity3          = 2, 2, 2




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

count = 1



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
        temperature1 = honey_dht11.temperature
        humidity1    = honey_dht11.humidity
    except Exception as e:
        print("Error with honey temperature and humidity sensor:", e)
        
    print("TempHoney: %d C" % temperature1 +' '+"HumidityHoney: %d %%" % humidity1)
         
    try: 
        temperature2 = brood_dht11.temperature
        humidity2    = brood_dht11.humidity
    except Exception as e:
        print("Error with honey temperature and humidity sensor:", e)

    print("TempBrood: %d C" % temperature2 +' '+"HumidityBrood: %d %%" % humidity2)

    try: 
        temperature3 = climate_dht11.temperature
        humidity3    = climate_dht11.humidity
    except Exception as e:
        print("Error with climate temperature and humidity sensor:", e)
        
    print("TempClimate: %d C" % temperature3 +' '+"HumidityClimate: %d %%" % humidity3)

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
        print()

        
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
        ssh.connect('137.63.185.94',username='hivemonitor', password= '')
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
    count = count + 1
    time.sleep(delay)

   
    print()
    print()
    print()