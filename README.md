# Structure

The repository contains 2 main modules i.e multimedia_capture and parameter_capture.

- Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

- Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

- support files has some testing files

- vibration_sensor and hx711.py are modules for the  accelerometor and weight sensors respectively


## SETTING UP FOR PARAMETER & MEDIA CAPTURE 

1. install git with ```sudo apt install git``` and Clone with 
```bash
git clone -b shawal-modularised https://github.com/ademnea/HiveMonitor2 monitor && cd monitor
```

2. Run ```sudo bash install.sh```

3. ```sudo raspi-config``` > interface options > I2C
  Enable for I2C for smbus
  
4. ```crontab -e``` , copy cronjobs from cron.txt and install them

5. Run ```python setup.py```

6. ```python main.py```



## SETTING UP TIME SYNCHRONIZATION
```pass```

