import matplotlib.pyplot as plt
import csv
import math

def plot_temperatures(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    time = [float(row[0]) for row in data]
    left_temp = [float(row[1]) for row in data]
    right_temp = [float(row[2]) for row in data]
    extra_temp = [float(row[3]) for row in data]

    plt.figure(figsize=(10, 6))
    plt.plot(time, left_temp, color='r', label='left plate')
    plt.plot(time, right_temp, color='b', label='right plate')
    plt.xlabel('time (s)')
    plt.ylabel('temperature')
    plt.title('plate temperatures')
    plt.legend()

    plt.figure(figsize=(10, 6))
    plt.plot(time, extra_temp, color='g', label='bag temp')
    plt.xlabel('time (seconds)')
    plt.ylabel('bag temperature')
    plt.title('bag temp')
    plt.legend()

    plt.show()

def map_range(value, old_min, old_max, new_min, new_max):
    return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min