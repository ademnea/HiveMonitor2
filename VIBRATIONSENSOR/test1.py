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