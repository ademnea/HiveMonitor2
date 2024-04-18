# SMART BEE MONITOR CONFIGURATION

This repository contains two main directories: `multimedia_capture` and `parameter_capture`.

- `multimedia_capture` is responsible for capturing audio, images, and videos, and transferring them to the server.
- `parameter_capture` is responsible for capturing temperature, humidity, carbon dioxide, and weight parameters, and sending them to the server.

## Setup for Parameter & Media Capture

Follow these steps to set up the environment:

1. Install the necessary Python packages:

    ```bash
    sudo pip3 install adafruit-circuitpython-dht paramiko sounddevice soundfile
    ```

2. Install the necessary system packages:

    ```bash
    sudo apt install libgpiod2 portaudio19-dev gpac
    ```

3. Update the configuration in `multimedia/config` with the correct values.

4. Enable the Pi camera module:

    ```bash
    sudo raspi-config
    ```

    Navigate to `Interface Options > Legacy Camera` and enable it for Pi camera module v3. If you're using a lower version, disable it. Reboot your Raspberry Pi after this step.

5. Set up the cron jobs:

    ```bash
    crontab -e
    ```

     Copy the cron jobs from `/support_files/cron.txt` and install them. Please note that these are just sample cronjobs and you have to chose the one most suitable for your current task.  

6. Insert the correct credentials in `measure_send_params.py` and `send_files_to_server.py`.

7. Go to `config.py` and set the correct node ID.

8. Configure the weight sensor by following the tutorial at [this link](https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/).

## 9. Setting Up Time Synchronization

The Raspberry Pi will use the time from the RTC. Make sure the RTC has a battery to maintain the correct time. Follow the tutorial at [this link](https://maker.pro/raspberry-pi/tutorial/how-to-add-an-rtc-module-to-raspberry-pi) to add an RTC module to your Raspberry Pi.

During the editing of `/lib/udev/hwclock-set`, clear the file and paste the following:

```bash
#!/bin/sh
# Reset the System Clock to UTC if the hardware clock from which it
# was copied by the kernel was in localtime.

HWCLOCKDEVICE="/dev/rtc0"

if [ -e /etc/default/hwclock ] ; then
    . /etc/default/hwclock
fi

if [ yes = "$BADYEAR" ] ; then
    /sbin/hwclock --rtc=$HWCLOCKDEVICE --systz --badyear
    /sbin/hwclock --rtc=$HWCLOCKDEVICE --hctosys --badyear
else
    /sbin/hwclock --rtc=$HWCLOCKDEVICE --systz
    /sbin/hwclock --rtc=$HWCLOCKDEVICE --hctosys
fi

# Note 'touch' may not be available in initramfs
# /run/udev/hwclock-set