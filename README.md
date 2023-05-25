The repository contains 2 main folders i.e multimedia_capture and parameter_capture.

Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

SETTING UP FOR PARAMETER CAPTURE

1.sudo pip3 install adafruit-circuitpython-dht

2.sudo pip3 install paramiko

3.sudo apt install libgpiod2

4.https://github.com/tatobari/hx711py.git

5. cd into hx711py and run python setup.py install

SETTING UP TIME SYNCHRONIZATION


