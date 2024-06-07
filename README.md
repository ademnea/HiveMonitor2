# SMART BEE MONITOR CONFIGURATION

This repository contains two main directories: `multimedia_capture` and `parameter_capture`.

- `multimedia_capture` is responsible for capturing audio, images, and videos, and transferring them to the server.
- `parameter_capture` is responsible for capturing temperature, humidity, carbon dioxide, and weight parameters, and sending them to the server.

## Setup for Parameter & Media Capture

Before installing the necessary Python packages, ensure you have the correct operating system installed on your Raspberry Pi:

- For Raspberry Pi Zero 2W, use the 32-bit legacy (Bullseye) version of Raspberry Pi OS.
- For Raspberry Pi 4 models, use the 64-bit legacy (Bullseye) version of Raspberry Pi OS.

Whether you install the OS with the desktop environment enabled is up to you, depending on your project's requirements.

Follow these steps to set up the environment:

1. Install the necessary Python packages:

    ```bash
    sudo pip3 install adafruit-circuitpython-dht paramiko sounddevice soundfile scipy sensirion_i2c_scd
    ```

2. Install the necessary system packages:

    ```bash
    sudo apt install libgpiod2 portaudio19-dev gpac libopenblas-base
    ```

3. Update the configuration in `multimedia/config` with the correct values.

4. Enable the Pi camera module:

    ```bash
    sudo raspi-config
    ```

    Navigate to `Interface Options > Legacy Camera` and enable it for Pi camera module v3. If you're using a lower version, disable it. Reboot your Raspberry Pi after this step.

5. **Activate the I2C Interface:**

    ```bash
    sudo raspi-config
    ```

    Navigate to `Interface Options > I2C` and enable it. This step is crucial for projects that require communication with I2C devices. Reboot your Raspberry Pi to apply the changes.

6. Set up the cron jobs:

    ```bash
    crontab -e
    ```

     Copy the cron jobs from `/support_files/cron.txt` and install them. Please note that these are just sample cronjobs and you have to chose the one most suitable for your current task.  

7. Insert the correct credentials in `measure_send_params.py` and `send_files_to_server.py`.

8. Go to `config.py` and set the correct node ID.

9. **Setting up the Microphone (I2S MEMS Microphone Breakout - SPH0645LM4H):**

    Follow the tutorial at [this link](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test) to set up the microphone.

10. Also add attribute pi_version and give it "2w", "0" depending on the version

11. Configure the weight sensor by following the tutorial at [this link](https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/).

## 11. Setting Up Time Synchronization

The Raspberry Pi will use the time from the RTC. Make sure the RTC has a battery to maintain the correct time. Follow the tutorial at [this link](https://maker.pro/raspberry-pi/tutorial/how-to-add-an-rtc-module-to-raspberry-pi) incase even after running the commands below , the pi still wakes up and has incorrect time. This will be reflected in the timestamps of the data sent when the pi reboots and sends data.

1. Update and upgrade your Raspberry Pi's package list and installed packages:

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

2. Install necessary packages for interfacing with the RTC module:

```bash
sudo apt-get install python3-smbus i2c-tools
```

3. Edit the Raspberry Pi configuration to enable the RTC module. Open the configuration file:

```bash
sudo nano /boot/config.txt
```

Then add one of the following lines to the end of the file, depending on the RTC chip you are using:

```plaintext
dtoverlay=i2c-rtc,ds1307
```

or

```plaintext
dtoverlay=i2c-rtc,pcf8523
```

or

```plaintext
dtoverlay=i2c-rtc,ds3231
```

4. Remove the `fake-hwclock` package and disable its service to prevent conflicts with the real RTC:

```bash
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock
```

5. Edit the `hwclock-set` script to ensure the system clock is correctly synchronized with the RTC at boot. Open the file:

```bash
sudo nano /lib/udev/hwclock-set
```

When the file opens, delete all its contents and replace with the following script:

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
```

6. Finally, write the current system time to the RTC to ensure it starts with the correct time:

```bash
sudo hwclock -w
```****