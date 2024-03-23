#! /usr/bin/python2

import time
import sys

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(2, 3)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(-15.144)
# hx.set_reference_unit(referenceUnit)
hx.reset()

hx.tare()

print("Tare done! Add weight now...")
while True:
    try:
        val = max(0,int(hx.get_weight(5)))
        weight=(val/1000)

        hx.power_down()
        hx.power_up()
        
        weight = round(weight, 2)##converting the weight to kgs
        print(weight)
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
