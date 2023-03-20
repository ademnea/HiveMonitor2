from os import path, mkdir
from hashlib import md5
import sqlite3
import time
import config
import device_capture_config
#import Adafruit_DHT
import sqlite3
import datetime 
from datetime import datetime
import sys
#from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
#from sensirion_i2c_scd import Scd4xI2cDevice
import time
  

# paths
video_dir = config.base_dir+"/multimedia/videos/"
audio_dir = config.base_dir+"/multimedia/audios/"


image_dir = config.base_dir+"/multimedia/images/"
hivein_dir = config.base_dir+"/mulitmedia/hivein/"
airquality_dir= config.base_dir+"/multimedia/airquality/"
# database_path = config.base_dir+"/multimedia/database.sqlite"


def recursive_mkdir(given_path):
    directories = given_path.split("/")
    length = len(directories)
    given_path, start_index = ("/" + directories[1], 2) if given_path[0] == '/' else (directories[0], 1)
    if not path.isdir(given_path):
        mkdir(given_path)

    for index in range(start_index, length):
        if len(directories[index]) > 0:
            given_path = given_path + '/' + directories[index]
            if not path.isdir(given_path):
                mkdir(given_path)


class Capture(device_capture_config.Capture):
    def __init__(self):
        super().__init__()
        self.files = []
        # last_slash = database_path.rindex('/')
        # database_directory = database_path[0:last_slash]

        # check if directories exist and if not create them
        if not path.isdir(video_dir):
            recursive_mkdir(video_dir)
        if not path.isdir(audio_dir):
            recursive_mkdir(audio_dir)
        if not path.isdir(image_dir):
            recursive_mkdir(image_dir)
       
        if not path.isdir(airquality_dir):
            recursive_mkdir(airquality_dir)
        # if not path.isdir(database_directory):
        #     recursive_mkdir(database_directory)

        # last_slash = database_path.rindex('/')
        # database_directory = database_path[0:last_slash]

        # check if directories exist and if not create them
        if not path.isdir(video_dir):
            recursive_mkdir(video_dir)
        if not path.isdir(audio_dir):
            recursive_mkdir(audio_dir)
        if not path.isdir(image_dir):
            recursive_mkdir(image_dir)
     
        if not path.isdir(airquality_dir):
            recursive_mkdir(airquality_dir)
        # if not path.isdir(database_directory):
        #     recursive_mkdir(database_directory)

        # conn = sqlite3.connect(database_path)
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # if cursor.fetchall().__str__().find('file') == -1:
        #     conn.execute('''create table file(
        #                     id integer primary key autoincrement not null,
        #                     file_name text unique not null,
        #                     file_path text not null ,
        #                     file_type text not null ,
        #                     hash_value text not null ,
        #                     transferred integer not null default 0
        #                 );''')
        #     conn.commit()
        # conn.close()

    # def save_to_db(self):
    #     start_time = time.time()
    #     # wait for video to save
    #     while int(time.time() - start_time) < 5:
    #         pass
    #     conn = sqlite3.connect(database_path)
    #     for file in self.files:
    #         try:
    #             conn.execute("insert into file (file_name, file_path, file_type, hash_value) values (?,?,?,?)",
    #                          (path.basename(file[0]), file[0], file[1], md5(open(file[0], 'rb').read()).hexdigest()))
    #             conn.commit()
    #         except sqlite3.IntegrityError:
    #             continue
    #     self.files = []
    #     conn.close()


if __name__ == "__main__":
    
    print()
    print()
    print()


    capture = Capture()

    timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print()


    print("DATE : " + timeString)
    print()

    print("TAKING PHOTOS")
    print()
    capture.snap(1)
    print()
    print()
    print()



    print("CAPTURING VIDEO")
    print()
    capture.record_video()
    print()
    print()
    print()

    print("CAPTURING AUDIO")
    print()
    capture.record_audio()
    print()
    print()
    print()




    ##time , date and database connection setup
e = datetime.now()
# cur = sqlite3.connect(database_path)
#unix= time.time()
#date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
# date= e.strftime("%Y-%m-%d %H:%M:%S")
# cur.execute("create table if not exists TEMP(DATE,TEMP1,HUM1,TEMP2,HUM2,TEMP4,HUM4,WEIGHT)")
# #temp1,temp2,humidity1,humidity2
# c = cur.cursor()
# ##



# ## HX711 set up
# EMULATE_HX711=False

# referenceUnit = 24.2

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
# hx.set_reference_unit(referenceUnit)

# hx.reset()

# hx.tare()
# ##end of HX711 set up


# ##data reading loop
# for i in range(0,4):
# # while True:
#     ##obtaining the weight 
#     sum_weight =  0
#     for i in range(3): #Setting a mean value for the weight we shall have read 
        
#         sample_weight = hx.get_weight(5)
#         sum_weight= sum_weight + sample_weight
    
#     weight = round(sum_weight/20000, 2)##converting the weight to kgs
        
#     print(weight, 'kg')
# #     hx.power_down()## put the hx711 to sleep


#     ##end of weight
        
#     #obtaining temperature humidity and temperature    
    
#     sensor = Adafruit_DHT.DHT11
#     humidity1, temperature1 = Adafruit_DHT.read_retry(sensor, 0)

#     print ("Temp1: {0:0.1f} C  Humidity1: {1:0.1f} %".format(temperature1, humidity1))
    
    
#     humidity2, temperature2 = Adafruit_DHT.read_retry(sensor, 6)

#     print ('Temp2: {0:0.1f} C  Humidity2: {1:0.1f} %'.format(temperature2, humidity2))
#     humidity4, temperature4 = Adafruit_DHT.read_retry(sensor, 12)

#     print ('Temp4: {0:0.1f} C  Humidity4: {1:0.1f} %'.format(temperature4, humidity4))
    
     
        

#     #Submit all  the findings to the database 
    
#     c.execute("insert into TEMP (DATE, TEMP1,HUM1,TEMP2,HUM2,TEMP4,HUM4,WEIGHT) values (?,?,?,?,?,?,?,?)",(date,temperature1,humidity1,temperature2,humidity2,temperature4,humidity4,weight))
#     cur.commit()
    
    
    
 
#     ##sending the data  to the server
    
    
# #     submit.foward()
    
#     time.sleep(2)
    
# #     ##  wake the hx711 to start reading
    
 
# #     scd41.set_automatic_self_calibration = True
# #     scd41.get_automatic_self_calibration
# with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
#     i2c_connection = I2cConnection(i2c_transceiver)    
#     scd41 = Scd4xI2cDevice(i2c_connection)
#     scd41.stop_periodic_measurement()
#     time.sleep(1)
#     scd41.reinit()
#     time.sleep(5)
#     scd41.start_periodic_measurement()
   
#     # Measure every 5 seconds
      
# #     while True:
#     for i in range(0,4):
#         time.sleep(5)
#         co2, temperature, humidity = scd41.read_measurement()
#         # use default formatting for printing output:
#         print("{}, {}, {}".format(co2, temperature, humidity))
#         # custom printing of attributes:
#         print("{:d} ppm CO2, {:0.2f} °C ({} ticks), {:0.1f} %RH ({} ticks)".format(
#             co2.co2,
#             temperature.degrees_celsius, temperature.ticks,
#             humidity.percent_rh, humidity.ticks))
#     scd41.stop_periodic_measurement()  

#     # start periodic measurement in high power mode
    
