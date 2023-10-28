import csv
import time
import board
import adafruit_adxl34x

def save_coordinates(x, y, z):
  with open('coordinates.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([x, y, z])

# Read the most recent saved coordinates from the file
def read_most_recent_coordinates():
  with open('coordinates.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    coordinates = []
    for row in reader:
      coordinates.append(row)
    return coordinates[-1]

# Compare the currently retrieved coordinates to the most recent saved coordinates
def compare_coordinates(current_coordinates, previous_coordinates):
  if current_coordinates[0] != previous_coordinates[0] or current_coordinates[1] != previous_coordinates[1] or current_coordinates[2] != previous_coordinates[2]:
    return True
  else:
    return False

# Get the current coordinates
current_coordinates = accelerometer.acceleration

# Read the most recent saved coordinates
previous_coordinates = read_most_recent_coordinates()

# Compare the coordinates
if compare_coordinates(current_coordinates, previous_coordinates):
  # The sensor has been moved
  print("The sensor has been moved!")
else:
  # The sensor has not been moved
  print("The sensor has not been moved.")

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# For ADXL343
#accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
accelerometer = adafruit_adxl34x.ADXL345(i2c)

accelerometer.enable_tap_detection()
# you can also configure the tap detection parameters when you enable tap detection:
# accelerometer.enable_tap_detection(tap_count=2,threshold=20, duration=50)

# Save the initial coordinates
save_coordinates(accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])

while True:
  # Get the current coordinates
  current_coordinates = accelerometer.acceleration

  # Read the most recent saved coordinates
  previous_coordinates = read_most_recent_coordinates()

  # Compare the coordinates
  if compare_coordinates(current_coordinates, previous_coordinates):
    # The sensor has been moved
    print("The sensor has been moved!")
  else:
    # The sensor has not been moved
    print("The sensor has not been moved.")

  time.sleep(1)