````markdown
# SMART BEE MONITOR RASPBERRY PI CONFIGURATION

This repository contains two main directories:  
`multimedia_capture` and `parameter_capture`.

- **`multimedia_capture`** handles the capture of audio, images, and videos, and transfers them to the server.  
- **`parameter_capture`** handles the capture of temperature, humidity, carbon dioxide (CO₂), and weight parameters, and sends them to the server.

---

## Setup for Parameter & Media Capture

Before installing the necessary Python packages, ensure you have the correct operating system installed on your Raspberry Pi:

- **Raspberry Pi Zero 2W:** Use the **32-bit legacy (Bullseye)** version of Raspberry Pi OS.  
- **Raspberry Pi 4 models:** Use the **64-bit legacy (Bullseye)** version of Raspberry Pi OS.

> Whether you install the desktop environment is up to you — it depends on your project’s requirements.

---

### Step 1: Install Required Python Packages
```bash
sudo pip3 install adafruit-circuitpython-dht paramiko sounddevice soundfile scipy sensirion_i2c_scd adafruit-circuitpython-bme680
````

---

### Step 2: Install Required System Packages

```bash
sudo apt install libgpiod2 portaudio19-dev gpac libopenblas-base
```

---

### Step 3: Configure Multimedia Capture

Update the configuration in:

```bash
multimedia_capture/config.py
```

with your correct server and device values.

---

### Step 4: Enable the Pi Camera Module

Run:

```bash
sudo raspi-config
```

Navigate to:

```
Interface Options > Legacy Camera
```

and enable it for Pi Camera Module v3.
If you’re using an older version, disable it instead.
Reboot after making changes.

---

### Step 5: Activate the I²C Interface

Run:

```bash
sudo raspi-config
```

Navigate to:

```
Interface Options > I2C
```

and enable it.
Reboot your Raspberry Pi to apply the changes.

---

### Step 6: Set Up Cron Jobs

Open the crontab:

```bash
crontab -e
```

Copy the cron jobs from:

```
/support_files/cron.txt
```

and install them.

> These are sample cron jobs — choose the ones most relevant to your setup.

---

### Step 7: Configure Credentials

Insert the correct credentials in:

* `measure_send_params.py`
* `send_files_to_server.py`

Then, in `config.py`, set the correct **node ID**.

---

### Step 8: Configure the Microphone (I2S MEMS Microphone Breakout - SPH0645LM4H)

Follow Adafruit’s tutorial to set up the microphone:
[ Adafruit I2S MEMS Microphone Tutorial](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test)

Also, add the `pi_version` attribute in your configuration —
set it to `"2w"`, `"0"`, etc., depending on your model.

---

### Step 9: Configure the Weight Sensor

Follow this tutorial to set up the HX711 weight sensor:
[ Digital Raspberry Pi Scale (HX711)](https://tutorials-raspberrypi.com/digital-raspberry-pi-scale-weight-sensor-hx711/)

---

## Step 10: Setting Up Time Synchronization

Your Raspberry Pi will use the Real-Time Clock (RTC) to maintain time — make sure the RTC has a working battery.

If the Pi still boots with the wrong time, follow this guide:
[ How to Add an RTC Module to Raspberry Pi](https://maker.pro/raspberry-pi/tutorial/how-to-add-an-rtc-module-to-raspberry-pi)

---

### 1️ Update & Upgrade Packages

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

### 2️ Install RTC Interface Packages

```bash
sudo apt-get install python3-smbus i2c-tools
```

### 3️ Enable the RTC Module

Edit the configuration:

```bash
sudo nano /boot/config.txt
```

Add one of the following at the end (depending on your RTC chip):

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

---

### 4️ Remove the Fake Hardware Clock

```bash
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock
```

---

### 5️ Edit the `hwclock-set` Script

Open:

```bash
sudo nano /lib/udev/hwclock-set
```

Replace all contents with:

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
```

---

### 6️ Write System Time to the RTC

```bash
sudo hwclock -w
```

---

## Alternative Setup: Using an Existing Configured SD Card

If you already have a working and fully configured Raspberry Pi SD card with the SMART BEE MONITOR setup, you can **clone it** and reuse the setup on other Raspberry Pis.
This is faster and guarantees identical software environments across multiple devices.

---

### Step 1: Identify the Source SD Card

Insert your **configured Raspberry Pi SD card** into your Linux computer and run:

```bash
lsblk
```

Find the device name (e.g., `/dev/sda` or `/dev/sdb`), usually around **29–32 GB** in size.

---

### Step 2: Unmount All Partitions

```bash
sudo umount /dev/sda*
```

---

### Step 3: Create the Image

```bash
sudo dd if=/dev/sda of=smartbee_backup.img bs=4M status=progress conv=fsync
sudo sync
```

> This command creates a full, bootable image of the SD card.
> It may take 10–30 minutes depending on SD card speed.

---

### Step 4: (Optional) Compress the Image

```bash
gzip smartbee_backup.img
```

This produces a smaller file named `smartbee_backup.img.gz`.

---

### 🧭 Step 5: Write the Image to Another SD Card

Insert the **target SD card** and identify it:

```bash
lsblk
```

Then unmount:

```bash
sudo umount /dev/sdb*
```

#### Write from the uncompressed image:

```bash
sudo dd if=smartbee_backup.img of=/dev/sdb bs=4M status=progress conv=fsync
```

#### Or write from the compressed image:

```bash
gunzip -c smartbee_backup.img.gz | sudo dd of=/dev/sdb bs=4M status=progress conv=fsync
```

Wait for completion, then flush writes:

```bash
sudo sync
```

---

### Step 6: (Optional) Expand Filesystem on the New SD Card

If the new SD card is larger than the original, expand the filesystem.

On the Raspberry Pi:

```bash
sudo raspi-config
# → Advanced Options → Expand Filesystem
```

Or manually on your computer:

```bash
sudo parted /dev/sdb resizepart 2 100%
sudo e2fsck -f /dev/sdb2
sudo resize2fs /dev/sdb2
```

---

### Step 7: Test the Clone

Insert the new SD card into your Raspberry Pi and boot it.
It should behave **identically** to the original setup.

---

### Notes

* Always double-check device names (`/dev/sda`, `/dev/sdb`) before using `dd`.
* Writing the wrong device will permanently erase its contents.
* This cloning method works for both **32-bit** and **64-bit** Raspberry Pi OS.
* After cloning, update the **node ID** in `config.py` if deploying multiple identical units.

---
