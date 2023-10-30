import csv

class ADXL345:
    def save_coordinates(x, y, z):
        with open('coordinates.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([x, y, z])
            csvfile.close()

    def subtract_lists(list_a, list_b):

        list_c = []
        for i in range(len(list_a)):
            list_c.append(list_a[i] - list_b[i])
        if list_c[0]>=6 and list_c[1] >=6 and list_c[2]>=6:
            return True
    
        else:
            return False


# Example usage:

#list_a = [1, 2, 3]
#list_b = [4, 5, 6]

#list_c = subtract_lists(list_a, list_b)

#print(list_c)

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