# client configurations
import os
# This is an auto-generated file
# You can edit these configurations directly or by running the setup.py script
# Note that errors in the config file can result into the failure of the whole client
# So be careful while editing, thanks 

from datetime import datetime
base_dir = os.pwd()

node_id = 2
username = "agatha"
password = "agatha"
base_dir = base_dir+"/multimedia_capture/"
picamera_version = 2 #specify the pi camera module version number (2 or 3) as of August 2023 
server_address = ""
image_url = "/var/www/html/ademnea_website/public/arriving_hive_media/"
audio_url = "/var/www/html/ademnea_website/public/arriving_hive_media/"
video_url =  "/var/www/html/ademnea_website/public/arriving_hive_media/"
remote_folder = "/var/www/html/ademnea_website/public/arriving_hive_media/"
timeString = datetime.now().strftime("%Y-%m-%d_%H%M%S")
logitude = ""
latitude = ""
TRANS_LIMIT = 100