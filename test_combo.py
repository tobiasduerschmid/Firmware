import os
import subprocess
import time
import pandas as pd
import json
import csv
from datetime import datetime

# Paths
ABSOLUTE_PATH_FIRMWARE = "/Users/jeaniechen/Desktop/CMU_REU/Firmware"
ABSOLUTE_PATH_MISSIONAPP = "/Users/jeaniechen/Desktop/CMU_REU/missionapp"
RELATIVE_PATH_FIRMWARE_TO_LOG_FOLDER = "./build/posix_sitl_default/tmp/rootfs/fs/microsd/log"

def main():

    # path to today's folder containing log files
    error_file_path = RELATIVE_PATH_FIRMWARE_TO_LOG_FOLDER + "/error_log.csv"
    s = datetime.today().strftime('%Y-%m-%d')
    today_log_folder = RELATIVE_PATH_FIRMWARE_TO_LOG_FOLDER + "/{}".format(s)

    # if csv file for logging errors/fails doesn't exist, create it
    if os.path.exists(error_file_path) == False:
        header = pd.DataFrame([['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type']])
        header.to_csv(error_file_path, index=False)

    exit_conditions = ["DANGEROUS BATTERY LEVEL", "Gyro #0 fail", "Error landing", "Error taking off", "Error arming drone", "Waiting for drone to be ready to arm", "Waiting for drone to connect"]
    
    # create csv file containing all configurations
    os.system("python3 generate_values.py")

    # read from file with all configurations and run one experiment for each line
    with open("all_combinations.csv") as csvfile:
        readCSV = csv.reader(csvfile)
        configurations = list(readCSV)
    
    # main loop for experiment, each row from the csv file is a configuration for one experiment
    for row in configurations:
        os.chdir(ABSOLUTE_PATH_FIRMWARE)
        acc = float(row[0])
        gyo = float(row[1])
        mag = float(row[2])
        prs = float(row[3])
        rotor = row[4]
        grav = {"x":0.0, "y":0.0, "z":9.80665}
        magF = {"x":float(row[8]), "y":float(row[9]), "z":float(row[10])}
        wind = {"x":float(row[11]), "y":float(row[12]), "z":float(row[13])}
        wd = {"x":float(row[14]), "y":float(row[15]), "z":float(row[16])}

        # write each row into config.json for simulator to parse
        x = {
            "sensor_noise_acc" : acc,
            "sensor_noise_gyo" : gyo,
            "sensor_noise_mag" : mag,
            "sensor_noise_prs" : prs,
            "rotor_orientation" : rotor,
            "gravity" : grav,   # don't change gravity
            "magnetic_field" : magF,
            "wind" : wind,
            "wind_deviation" : wd
        }    
        # create and write to json file
        with open("./config.json", 'w') as f:
            json.dump(x, f, indent=4)

        # start px4 and jmavsim, jmavsim will read from config.json and change its environment accordingly
        px4 = subprocess.Popen(['make', 'posix_sitl_default', 'jmavsim'], stdout=subprocess.PIPE)

        # wait for a bit for px4 to get ready before starting mission
        time.sleep(10)
        os.chdir(ABSOLUTE_PATH_MISSIONAPP)
        os.system("make")
        mission = subprocess.Popen(['./missionapp', '--enforcer=ElasticEnforcer', 'udp://'], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        os.chdir(ABSOLUTE_PATH_FIRMWARE)

        error = False
        num_arming = 0
        num_connect = 0
        gyro_fail = 0
        # read terminal output from missionapp
        for line in mission.stdout:
            print(line.rstrip())
            if any(x in line for x in exit_conditions):
                if "Waiting for drone to connect" in line:
                    num_connect = num_connect + 1
                    # if connecting hangs
                    if num_connect > 40:
                        # append to error_log.csv
                        # create dataframe
                        data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                                wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "PX4 connecting hangs"]
                        df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                        'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                        'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                        'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                        with open(error_file_path, "a") as f:
                            df.to_csv(f, encoding='utf-8', index=False, header=False)
                        # kill px4, jmavsim, and mission
                        os.system("pkill -x px4")
                        px4.kill()
                        mission.kill()
                        error = True
                        break

                if "Waiting for drone to be ready to arm" in line:
                    num_arming = num_arming + 1
                    # if arming hangs
                    if num_arming > 40:
                        # append to error_log.csv
                        # create dataframe
                        data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                                wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Arming hangs"]
                        df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                        'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                        'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                        'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                        with open(error_file_path, "a") as f:
                            df.to_csv(f, encoding='utf-8', index=False, header=False)
                        # kill px4, jmavsim, and mission
                        os.system("pkill -x px4")
                        px4.kill()
                        mission.kill()
                        error = True
                        # get rid of log file
                        os.chdir(today_log_folder)
                        # remove ulog files before creating one
                        os.system("rm *.ulg")
                        break

                if "DANGEROUS BATTERY LEVEL" in line:
                    # append to error_log.csv
                    # create dataframe
                    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Dangerous battery level"]
                    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                    'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                    'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                    'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                    with open(error_file_path, "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    os.chdir(today_log_folder)
                    # remove all csv and ulog files before creating one
                    os.system("rm *.ulg")
                    break

                if "Gyro #0 fail" in line:
                    gyro_fail = gyro_fail + 1
                    # if connecting hangs
                    if gyro_fail > 15:
                        # append to error_log.csv
                        # create dataframe
                        data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                                wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Gyro fail"]
                        df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                        'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                        'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                        'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                        with open(error_file_path, "a") as f:
                            df.to_csv(f, encoding='utf-8', index=False, header=False)
                        # kill px4, jmavsim, and mission
                        os.system("pkill -x px4")
                        px4.kill()
                        mission.kill()
                        error = True
                        # get rid of log file
                        os.chdir(today_log_folder)
                        # remove all csv and ulog files before creating one
                        os.system("rm *.ulg")
                        break

                if "Error landing" in line:
                    # append to error_log.csv
                    # create dataframe
                    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Landing"]
                    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                    'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                    'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                    'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                    with open(error_file_path, "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    os.chdir(today_log_folder)
                    # remove all csv and ulog files before creating one
                    os.system("rm *.ulg")
                    break
                
                if "Error taking off" in line:
                    # append to error_log.csv
                    # create dataframe
                    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Takeoff"]
                    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                    'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                    'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                    'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                    with open(error_file_path, "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    os.chdir(today_log_folder)
                    # remove all csv and ulog files before creating one
                    os.system("rm *.ulg")
                    break
                
                if "Error arming drone" in line:
                    # append to error_log.csv
                    # create dataframe
                    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Arming"]
                    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                    'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                    'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                    'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                    with open(error_file_path, "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    os.chdir(today_log_folder)
                    # remove all csv and ulog files before creating one
                    os.system("rm *.ulg")
                    break

        if error == False:
            # wait for mission to end
            mission.communicate()
            os.system("python data_organize.py")
            # kill px4, jmavsim, and mission
            os.system("pkill -x px4")
            px4.kill()
            mission.kill()


if __name__ == "__main__":
    main()