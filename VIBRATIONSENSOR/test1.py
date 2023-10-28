import time
import board
import adafruit_adxl34x

from ADXL345 import ADXL345

i2c = board.I2C()  # uses board.SCL and board.SDA

# For ADXL343
#accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)



# # Get the current coordinates
# current_coordinates = accelerometer.acceleration

# # Read the most recent saved coordinates
# previous_coordinates = read_most_recent_coordinates()

# # Compare the coordinates
# if compare_coordinates(current_coordinates, previous_coordinates):
#   # The sensor has been moved
#   print("The sensor has been moved!")
# else:
#   # The sensor has not been moved
#   print("The sensor has not been moved.")

# Save the initial coordinates
ADXL345.save_coordinates(accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])

# while True:
#   # Get the current coordinates
#   current_coordinates = accelerometer.acceleration

#   # Read the most recent saved coordinates
#   previous_coordinates = read_most_recent_coordinates()

#   # Compare the coordinates
#   if compare_coordinates(current_coordinates, previous_coordinates):
#     # The sensor has been moved
#     print("The sensor has been moved!")
#   else:
#     # The sensor has not been moved
#     print("The sensor has not been moved.")

#   time.sleep(1)