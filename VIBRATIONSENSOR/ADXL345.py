import csv

class ADXL345:
    def save_coordinates(x, y, z):
        with open('coordinates.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([x, y, z])
            csvfile.close()


    # Read the most recent saved coordinates from the file
    def read_most_recent_coordinates():
        with open('coordinates.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            coordinates = []
            
            for row in reader:
                coordinates.append(row[-1])
            csvfile.close()
        return coordinates

    # Compare the currently retrieved coordinates to the most recent saved coordinates
    def compare_coordinates(current_coordinates, previous_coordinates):
        if current_coordinates[0] != previous_coordinates[0] or current_coordinates[1] != previous_coordinates[1] or current_coordinates[2] != previous_coordinates[2]:
            return True
        else:
            return False