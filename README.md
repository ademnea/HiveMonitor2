The repository contains 2 main folders i.e multimedia_capture and parameter_capture.

Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

SETTING UP FOR PARAMETER & MEDIA CAPTURE 


steps to verify multi-media capture
//install python3-venv
1.sudo apt update 
2.sudo apt install python3-venv
3.sudo apt install portaudio19-dev

//create a virtual environment but incase you already created on ,you cant go straight to activating it
3.python3 -m venv ~/hivemonitor-env

//activate the virtual envinronment
4.source ~/hivemonitor-env/bin/activate

//to enable camera settings
sudo raspi-config nonint do_legacy 0
sudo reboot

//install sounddevice within the virtual environment
5.pip install sounddevice 

//install soundfile module
6.pip install soundfile

//install numpy module
pip install numpy

//install GPAC for the MP4Box
//build it from source
7.sudo apt update
8.sudo apt install build-essential git pkg-config libfreetype6-dev libfontconfig1-dev libgl1-mesa-dev libegl1-mesa-dev libgles2-mesa-dev libsdl2-dev libcurl4-openssl-dev libmad0-dev libjpeg-dev libpng-dev libx11-dev

//clone the GPAC repository
9.git clone https://github.com/gpac/gpac.git

//navigate to GPAC directory
cd gpac

//configure the build
./configure

//build and install GPAC
make -j4
sudo make install

sudo apt install gpa

//verify the installation
python -c "import sounddevice"

1.sudo pip3 install adafruit-circuitpython-dht

2.sudo pip3 install paramiko

3.sudo apt install libgpiod2

4.sudo apt-get install portaudio19-dev

5.sudo apt install gpac

6.sudo pip3 install sounddevice

7.sudo pip3 install soundfile

8.Edit this line "import device_capture_config as device_capture" in capture.py 
  depending on the pi camera to be used whether old or new.

9.sudo raspi-config > interface options > Legacy camera
  Enable for pi camera module v3 , if lower version , disable
  Reboot after 
  
10.crontab -e , copy cronjobs from cron.txt and install them

11.insert credentials in measure_send_params.py and send_files_to_server.py 

12.go to config.py and set the correct node id






SETTING UP TIME SYNCHRONIZATION


