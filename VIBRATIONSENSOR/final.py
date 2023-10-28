import csv

with open('coordinates.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    coordinates = []
    for row in reader:
        coordinates.append(row[-1])
    csvfile.close()

print(coordinates)