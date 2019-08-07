import pandas as pd
import glob
import os
import time
import json
import random
from datetime import datetime

def generate_mag_values(start, stop):
    temp_dict = {}
    # generate random values in range start to stop and add to list
    # maybe use random.randrange()?
    rand_list = []
    for i in range(3):
        num = '%.3f'%(random.uniform(start, stop))
        rand_list.append(float(num))
    # create dictionary
    temp_dict["x"] = rand_list[0]
    temp_dict["y"] = rand_list[1]
    temp_dict["z"] = rand_list[2]
    return temp_dict

def generate_wind_values(start, stop):
    temp_dict = {}
    # generate random values in range start to stop and add to list
    rand_list = []
    for i in range(3):
        num = float(random.randrange(start, stop))/10
        rand_list.append(num)
    # create dictionary
    temp_dict["x"] = rand_list[0]
    temp_dict["y"] = rand_list[1]
    temp_dict["z"] = rand_list[2]
    return temp_dict

def main():
    # can use random.choice() to choose random element from list
    # space of values for each parameter
    # deactivate_sensor_values = [True, False]
    sensor_noise_acc = '%.3f'%(random.uniform(0.01, 0.1))
    sensor_noise_gyo = '%.3f'%(random.uniform(0.001, 0.09))
    sensor_noise_mag = '%.3f'%(random.uniform(0.0001, 0.01))
    sensor_noise_prs = '%.3f'%(random.uniform(0.01, 0.9))
    rotor_orientation_values = ["+", "x"]
    # earth, moon, mars, jupiter, pluto, sun
    gravity_values = [{"x":0.0, "y":0.0, "z":9.80665}, 
                    {"x":0.0, "y":0.0, "z":1.62}, 
                    {"x":0.0, "y":0.0, "z":3.711}, 
                    {"x":0.0, "y":0.0, "z":24.79}, 
                    {"x":0.0, "y":0.0, "z":0.62}, 
                    {"x":0.0, "y":0.0, "z":274.0}]
    # simulator's default, random values
    # earth's surface magnetic field magnitude ranges from 0.25 to 0.65 gauss
    magnetic_field_values = [{"x" : 0.21523, "y" : 0.0, "z" : 0.42741}]
    wind_values = []
    wind_deviation_values = []

    # add random values to magnetic field dictionary
    for i in range(15):
        d = generate_mag_values(0.00, 0.65)
        magnetic_field_values.append(d)

    # populate wind_values with random values
    for i in range(15):
        d = generate_wind_values(0, 200)
        wind_values.append(d)

    # populate wind_deviation with random values
    for i in range(15):
        d = generate_wind_values(0, 100)
        wind_deviation_values.append(d)

    # Prob need to have a bunch of for loops to try every possible combo of values later
    # create random json string
    # a = random.choice(deactivate_sensor_values)
    b = random.choice(rotor_orientation_values)
    # c = random.choice(gravity_values)
    d = random.choice(magnetic_field_values)
    e = random.choice(wind_values)
    f = random.choice(wind_deviation_values)
    x = {
        # "deactivate_sensors" : a,
        "sensor_noise_acc" : float(sensor_noise_acc),
        "sensor_noise_gyo" : float(sensor_noise_gyo),
        "sensor_noise_mag" : float(sensor_noise_mag),
        "sensor_noise_prs" : float(sensor_noise_prs),
        "rotor_orientation" : b,
        "gravity" : {"x":0.0, "y":0.0, "z":9.80665},   # don't change gravity
        "magnetic_field" : d,
        "wind" : e,
        "wind_deviation" : f
    }

    # create and write to json file
    with open("config.json", 'w') as f:
        json.dump(x, f, indent=4)


if __name__ == "__main__":
    # os.system("open -a QGroundControl")
    os.chdir("/Users/jeanie/Desktop/Firmware")
    main()
    os.system("make posix_sitl_default jmavsim")
    
