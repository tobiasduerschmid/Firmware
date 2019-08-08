import pandas as pd
import os.path
import glob
import os
import time
import json
from datetime import datetime

def main():
    # Create 1 row dataframe for each mission
    list1 = glob.glob('*_battery_status_*.csv')
    list2 = glob.glob('*_vehicle_land_detected_*.csv')
    list3 = glob.glob('*_vehicle_status_0.csv')
    time = pd.read_csv("time.csv")

    # get duration
    duration = time.at[0, 'Duration']
    #print(duration)
    hour = int(duration[0], 10)
    minute = int(duration[2:4], 10)
    seconds = int(duration[5:7], 10)
    millisec_duration = hour*60*60*1000 + minute*60*1000 + seconds*1000

    # turn battery status csv into dataframe with only the "remaining" column
    battery = pd.read_csv(list1[0], usecols=['remaining'])
    # remove last 2 rows (they are increasing)
    battery_status = battery.iloc[:-2]

    # turn vehicle_land_detected csv into dataframe with only the "ground contact" column
    ground_contact = pd.read_csv(list2[0], usecols=['ground_contact'])

    # turn vehicle_status csv into dataframe with only the 'engine_failure', 'mission_failure', 'failure_detector_status' columns
    vehicle_status = pd.read_csv(list3[0], usecols=['engine_failure', 'mission_failure', 'failure_detector_status'])

    # calculate battery percent used
    numRows = len(battery_status.index)
    battery_used = battery_status.at[0,'remaining'] - battery_status.at[numRows-1, 'remaining']

    # count how many times the vehicle had ground contact
    frequency = ground_contact['ground_contact'].value_counts()
    num_ground_contacts = frequency.get(key=1) if len(frequency) == 2 else 0

    # count how many times vehicle had engine_failure, mission_failure, and the failure_detector_status
    engine = vehicle_status['engine_failure'].value_counts()
    engine_fails = engine.get(key=1) if len(engine) == 2 else 0
    mission = vehicle_status['mission_failure'].value_counts()
    mission_fails = mission.get(key=1) if len(mission) == 2 else 0
    detector = vehicle_status['failure_detector_status'].value_counts()
    failures_detected = detector.get(key=1) if len(mission) == 2 else 0

    # read config.json and add those environment variables to csv file
    os.chdir("/Users/jeanie/Desktop/Firmware")
    with open("./config.json") as json_file:
        data = json.load(json_file)
        acc = data["sensor_noise_acc"]
        gyo = data["sensor_noise_gyo"]
        mag = data["sensor_noise_mag"]
        prs = data["sensor_noise_prs"]
        rotor = data["rotor_orientation"]
        grav = data["gravity"]
        magF = data["magnetic_field"]
        wind = data["wind"]
        wd = data["wind_deviation"]
        

    # create dataframe
    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], millisec_duration, battery_used, 
            num_ground_contacts, engine_fails, mission_fails, failures_detected]
    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Duration (millisec)', 
                                'Battery Consumption', 'Number of Ground Contacts', 
                                'Number of Engine Failures', 'Number of Mission Failures', 'Number of Failures Detected'])

    # remove all csv and ulog files before creating one
    s = datetime.today().strftime('%Y-%m-%d')
    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
    os.system("rm *.csv *.ulg")

    # if csv file doesn't exist, create it
    if os.path.exists("../missions.csv") == False:
        header = pd.DataFrame([['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Duration (millisec)', 
                                'Battery Consumption', 'Number of Ground Contacts', 
                                'Number of Engine Failures', 'Number of Mission Failures', 'Number of Failures Detected']])
        header.to_csv("../missions.csv", index=False)

    # append dataframe as row to csv file
    with open("../missions.csv", "a") as f:
        df.to_csv(f, encoding='utf-8', index=False, header=False)

if __name__ == "__main__":
    s = datetime.today().strftime('%Y-%m-%d')
    # call pyulog to create time.csv and all other csv files
    # os.chdir("/Users/jeaniechen/Documents/QGroundControl/Logs")
    # os.chdir("./build/px4_sitl_default/tmp/rootfs/log/%s" % s)
    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
    file = glob.glob('*.ulg')
    ulg_info = "ulog_info {}".format(file[0])
    os.system(ulg_info)
    time.sleep(7)
    ulg_to_csv = "ulog2csv {}".format(file[0])
    os.system(ulg_to_csv)
    main()
    