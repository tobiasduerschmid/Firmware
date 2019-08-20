import pandas as pd
import glob
import os
import json
import random
from datetime import datetime
import itertools
import random

# itertools.product() to create all possible combinations of values
NUM_CONFIGURATIONS = 500     # also the number of experiments we want to run

def main():
    # define the space for each environment variable
    sensor_acc = [0.01, 0.16, 0.64, 1.28]
    sensor_gyo = [0.001, 0.016, 0.128, 0.512, 1.024]
    sensor_mag = [0.0001, 0.0016, 0.0128, 0.0512, 0.1024]
    sensor_prs = [0.01, 0.16, 0.64, 1.28]
    rotor_orientation_values = ["+", "x"]
    gravity_x = 0.0
    gravity_y = 0.0
    gravity_z = 9.80665
    mag_x = [0.21523, 0.0, 0.4, 0.65]
    mag_y = [0.0, 0.2, 0.65]
    mag_z = [0.42741, 0.0, 0.2, 0.65]
    wind_x = [0.0, 1.0, 10.0, 20.0]
    wind_y = [0.0, 1.0, 10.0, 20.0]
    wind_z = [0.0, 1.0, 10.0, 20.0]
    wind_deviation_x = [0.0, 1.0, 10.0]
    wind_deviation_y = [0.0, 1.0, 10.0]
    wind_deviation_z = [0.0, 1.0, 10.0]

    # all possible combinations
    # all_lists = [sensor_acc, sensor_gyo, sensor_mag, sensor_prs, rotor_orientation_values, 
    #             gravity_x, gravity_y, gravity_z, mag_x, mag_y, mag_z, wind_x, wind_y, wind_z,
    #             wind_deviation_x, wind_deviation_y, wind_deviation_z]
    # cartesian product of all lists
    # combinations = list(itertools.product(*all_lists))

    # don't create all possible combos but just sample n number of combos
    sample = []
    for i in range(NUM_CONFIGURATIONS):
        flag = False
        while flag == False:
            x = []
            a = random.choice(sensor_acc)
            x.append(a)
            b = random.choice(sensor_gyo)
            x.append(b)
            c = random.choice(sensor_mag)
            x.append(c)
            d = random.choice(sensor_prs)
            x.append(d)
            e = random.choice(rotor_orientation_values)
            x.append(e)
            x.append(gravity_x)
            x.append(gravity_y)
            x.append(gravity_z)
            f = random.choice(mag_x)
            x.append(f)
            g = random.choice(mag_y)
            x.append(g)
            h = random.choice(mag_z)
            x.append(h)
            i = random.choice(wind_x)
            x.append(i)
            j = random.choice(wind_y)
            x.append(j)
            k = random.choice(wind_z)
            x.append(k)
            l = random.choice(wind_deviation_x)
            x.append(l)
            m = random.choice(wind_deviation_y)
            x.append(m)
            n = random.choice(wind_deviation_z)
            x.append(n)
            if x not in sample:
                flag = True
        # add new list of values to sample
        sample.append(x)

    # randomly sample 500 configurations
    # sample = []
    # for i in range(500):
    #     flag = False
    #     while flag == False:
    #         x = random.choice(combinations)
    #         if x not in sample:
    #             flag = True
    #     sample.append(x)

    # write to file
    with open("all_combinations.csv", "w") as f:
        for x in sample:
            line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16])
            f.write(line)


if __name__ == "__main__":
    main()