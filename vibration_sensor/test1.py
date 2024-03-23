import os
import time
import board
import adafruit_adxl34x

from ADXL345 import ADXL345

i2c = board.I2C()  # uses board.SCL and board.SDA

# For ADXL343
#accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)


# Get the current coordinates
current_coordinates = accelerometer.acceleration

# Check if the coordinates file exists
if not os.path.exists('coordinates.csv'):
    # Create the coordinates file
    ADXL345.save_coordinates(accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])
 
# Read the most recent saved coordinates
previous_coordinates = ADXL345.read_most_recent_coordinates()

print(previous_coordinates)
# Compare the coordinates
if ADXL345.compare_coordinates(current_coordinates, previous_coordinates) and ADXL345.subtract_lists(current_coordinates , previous_coordinates) :
  # The sensor has been moved
  print("The sensor has been moved!")
else:
  # The sensor has not been moved
  print("The sensor has not been moved.")
