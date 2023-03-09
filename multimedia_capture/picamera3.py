#This file is used for testing raspcamera configurations before implemeting them in the actual code
#The scripts than run this camera are got from the official documentation of rasp camera module 3

import subprocess

# Run the command and capture the output and errors
#result = subprocess.run(["libcamera-jpeg", "-o", "/home/pi/Desktop/Intergrated-System/Adafruit_Python_DHT/test2.jpg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
video_result = subprocess.run(["libcamera-vid", "-t","10000", "-o", "/home/pi/Desktop/RaspcaptureIntegrated/multimedia/videos/test.h264", "--width", "1920", "--height", "1080", "-f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# Print the output and errors (if any)
print(video_result.stdout.decode("utf-8"))
print(video_result.stderr.decode("utf-8"))
