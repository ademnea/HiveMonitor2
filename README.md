The repository contains 2 main folders i.e multimedia_capture and parameter_capture.

Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

SETTING UP FOR PARAMETER CAPTURE

cd parameter_capture

git clone https://github.com/adafruit/Adafruit_Python_DHT.git

cd Adafruit_Python_DHT/

sudo python3 setup.py install

DONE...For more inquiries visit https://github.com/adafruit/Adafruit_Python_DHT



sudo pip3 install adafruit-circuitpython-dht


SETTING UP TIME SYNCHRONIZATION

sudo apt-get update
sudo apt-get install ntp

sudo nano /etc/ntp.conf

add these lines below;
server 0.ke.pool.ntp.org
server 3.africa.pool.ntp.org
server 2.africa.pool.ntp.org


