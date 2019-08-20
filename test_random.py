import os
import subprocess
import time
import pandas as pd
import json
from datetime import datetime

# Paths
ABSOLUTE_PATH_FIRMWARE = "/Users/jeaniechen/Desktop/CMU_REU/Firmware"
ABSOLUTE_PATH_MISSIONAPP = "/Users/jeaniechen/Desktop/CMU_REU/missionapp"
RELATIVE_PATH_FIRMWARE_TO_LOG_FOLDER = "./build/posix_sitl_default/tmp/rootfs/fs/microsd/log"
NUM_EXPERIMENTS = 300

def main():

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
    
    # can change the number of simulations
    for i in range(NUM_EXPERIMENTS):
        os.chdir(ABSOLUTE_PATH_FIRMWARE)
        px4 = subprocess.Popen(['python', 'run.py'], stdout=subprocess.PIPE)
        
        # store config file variables
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
            # time.sleep(15)
            # kill px4, jmavsim, and mission
            os.system("pkill -x px4")
            px4.kill()
            mission.kill()


if __name__ == "__main__":
    main()