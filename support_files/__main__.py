import subprocess
import time

# start capturing images, videos and audios
subprocess.run(["python3", "/home/pi/Desktop/HiveMonitor2/multimedia_capture/capture.py"])

# # wait 
# time.sleep(60)

# send captured files to server
subprocess.run(["python3", "/home/pi/Desktop/HiveMonitor2/multimedia_capture/send_files_to_server.py"])


# start capturing temperature, humidity, carbondioxide and weight and send to the server
subprocess.run(["python3", "/home/pi/Desktop/HiveMonitor2/parameter_capture/measure_send_params.py"])

