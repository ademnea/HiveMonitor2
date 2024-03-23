# Structure

The repository contains 2 main modules i.e multimedia_capture and parameter_capture.

- Multimedia capture is in charge of capturing audio, image and videos and transfering 
them to the server.

- Parameter capture is in charge of capturing temperature, humidity , carbondioxide and 
weight parameters and sending them to the server.

- support files has some testing files

- vibration_sensor and hx711.py are modules for the  accelerometor and weight sensors respectively


## SETTING UP FOR PARAMETER & MEDIA CAPTURE 

1. Run ```bash install.sh```

2. ```sudo raspi-config``` > interface options > I2C
  Enable for I2C for smbus
  
3. ```crontab -e``` , copy cronjobs from cron.txt and install them

4. Run ```python setup.py```

5. ```python main.py```



## SETTING UP TIME SYNCHRONIZATION
```pass```

