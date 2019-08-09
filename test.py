import os
import subprocess
import time
import pandas as pd
import json
from datetime import datetime

def main():

    # make posix jmavsim for the first time
    os.chdir("/Users/jeanie/Desktop/Firmware")
    os.system("make posix_sitl_default jmavsim")
    time.sleep(15)
    os.system("pkill -x px4")

    
    # if csv file for logging errors/fails doesn't exist, create it
    if os.path.exists("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv") == False:
        header = pd.DataFrame([['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type']])
        header.to_csv("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", index=False)

    exit_conditions = ["Dangerous battery level!", "Error landing", "Error taking off", "Error arming drone", "Waiting for drone to be ready to arm"]
    
    # can change the number of simulations
    for i in range(1):
        os.chdir("/Users/jeanie/Desktop/Firmware")
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
        time.sleep(15)
        os.chdir("/Users/jeanie/Desktop/missionapp")
        os.system("make")
        mission = subprocess.Popen(['./missionapp', '--enforcer=ElasticEnforcer', 'udp://'], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        os.chdir("/Users/jeanie/Desktop/Firmware")
        # mission = subprocess.Popen(['python', 'mission.py'], 
        #                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        error = False
        num_arming = 0
        # read terminal output from missionapp
        for line in mission.stdout:
            print(line.rstrip())
            if any(x in line for x in exit_conditions):
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
                        with open("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", "a") as f:
                            df.to_csv(f, encoding='utf-8', index=False, header=False)
                        # kill px4, jmavsim, and mission
                        # os.chdir("./build/px4_sitl_default/bin")
                        # os.system("./px4-shutdown")
                        # kill posix/px4?
                        os.system("pkill -x px4")
                        px4.kill()
                        mission.kill()
                        error = True
                        # get rid of log file
                        s = datetime.today().strftime('%Y-%m-%d')
                        os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
                        # remove ulog files before creating one
                        os.system("rm *.ulg")
                        break

                if "Dangerous battery level!" in line:
                    # append to error_log.csv
                    # create dataframe
                    data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                            wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Dangerous battery level"]
                    df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                    'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                    'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                    'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error Type'])
                    with open("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    # os.chdir("./build/px4_sitl_default/bin")
                    # os.system("./px4-shutdown")
                    # kill posix/px4?
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    s = datetime.today().strftime('%Y-%m-%d')
                    # os.chdir("../tmp/rootfs/log/%s" % s)
                    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
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
                    with open("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    # os.chdir("./build/px4_sitl_default/bin")
                    # os.system("./px4-shutdown")
                    # kill posix/px4?
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    s = datetime.today().strftime('%Y-%m-%d')
                    # os.chdir("../tmp/rootfs/log/%s" % s)
                    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
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
                    with open("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    # os.chdir("./build/px4_sitl_default/bin")
                    # os.system("./px4-shutdown")
                    # kill posix/px4?
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    s = datetime.today().strftime('%Y-%m-%d')
                    # os.chdir("../tmp/rootfs/log/%s" % s)
                    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
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
                    with open("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/error_log.csv", "a") as f:
                        df.to_csv(f, encoding='utf-8', index=False, header=False)
                    
                    # kill px4, jmavsim, and mission
                    # os.chdir("./build/px4_sitl_default/bin")
                    # os.system("./px4-shutdown")
                    # kill posix/px4?
                    os.system("pkill -x px4")
                    px4.kill()
                    mission.kill()
                    error = True
                    # get rid of log file
                    s = datetime.today().strftime('%Y-%m-%d')
                    # os.chdir("../tmp/rootfs/log/%s" % s)
                    os.chdir("./build/posix_sitl_default/tmp/rootfs/fs/microsd/log/%s" % s)
                    # remove all csv and ulog files before creating one
                    os.system("rm *.ulg")
                    break

        if error == False:
            # wait for mission to end
            mission.communicate()
            os.system("python data_organize.py")
            # time.sleep(15)
            # kill px4, jmavsim, and mission
            # os.chdir("./build/px4_sitl_default/bin")
            # os.system("./px4-shutdown")
            # kill posix/px4?
            os.system("pkill -x px4")
            px4.kill()
            mission.kill()


if __name__ == "__main__":
    main()