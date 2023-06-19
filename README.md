The repository contains 2 main folders i.e multimedia_capture and parameter_capture.

Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

SETTING UP FOR PARAMETER & MEDIA CAPTURE 

1.sudo pip3 install adafruit-circuitpython-dht

2.sudo pip3 install paramiko

3.sudo apt install libgpiod2

4.sudo apt-get install portaudio19-dev

5.sudo apt install gpac

6.Edit this line "import device_capture_config as device_capture" in capture.py 
  depending on the pi camera to be used whether old or new.

7.sudo raspi-config > interface options > Legacy camera
  Enable for pi camera module v3 , if lower version , disable
  Reboot after this


SETTING UP TIME SYNCHRONIZATION


