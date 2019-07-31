import os
import subprocess
import time
import pandas as pd
import json

def main():
    # if csv file for logging errors/fails doesn't exist, create it
    if os.path.exists("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv") == False:
        header = pd.DataFrame([['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error']])
        header.to_csv("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv", index=False)

    exit_conditions = ["Dangerous battery level!", "Error landing", "Error taking off", "Error arming drone"]
    # px4 = subprocess.Popen(['make', 'px4_sitl', 'jmavsim'], stdout=subprocess.PIPE)
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
    # os.chdir("/Users/jeaniechen/Desktop/CMU_REU/missionapp")
    # mission = subprocess.Popen(['./missionapp', '--enforcer=ElasticEnforcer', 'udp://'], 
    #                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    # os.chdir("/Users/jeaniechen/Desktop/CMU_REU/Firmware")
    mission = subprocess.Popen(['python', 'mission.py'], 
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    error = False
    for line in mission.stdout:
        print(line.rstrip())
        if any(x in line for x in exit_conditions):
            if "Dangerous battery level!" in line:
                # append to error_log.csv
                # create dataframe
                data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                        wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Dangerous battery level"]
                df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error'])
                with open("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv", "a") as f:
                    df.to_csv(f, encoding='utf-8', index=False, header=False)
                
                # kill px4, jmavsim, and mission
                px4.kill()
                mission.kill()
                error = True
                break

            if "Error landing" in line:
                # append to error_log.csv
                # create dataframe
                data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                        wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Landing"]
                df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error'])
                with open("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv", "a") as f:
                    df.to_csv(f, encoding='utf-8', index=False, header=False)
                
                # kill px4, jmavsim, and mission
                px4.kill()
                mission.kill()
                error = True
                break
            
            if "Error taking off" in line:
                # append to error_log.csv
                # create dataframe
                data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                        wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Takeoff"]
                df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error'])
                with open("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv", "a") as f:
                    df.to_csv(f, encoding='utf-8', index=False, header=False)
                
                # kill px4, jmavsim, and mission
                px4.kill()
                mission.kill()
                error = True
                break
            
            if "Error arming drone" in line:
                # append to error_log.csv
                # create dataframe
                data = [acc, gyo, mag, prs, rotor, grav["x"], grav["y"], grav["z"], magF["x"], magF["y"], magF["z"], 
                        wind["x"], wind["y"], wind["z"], wd["x"], wd["y"], wd["z"], "Arming"]
                df = pd.DataFrame([data], columns=['Sensor Noise Accelerometer', 'Sensor Noise Gyroscope', 'Sensor Noise Magnetometer', 
                                'Sensor Noise Pressure', 'Rotor Orientation', 'Gravity_x', 'Gravity_y', 'Gravity_z', 
                                'Magnetic Field_x', 'Magnetic Field_y', 'Magnetic Field_z', 'Wind_x', 'Wind_y', 'Wind_z', 
                                'Wind Deviation_x', 'Wind Deviation_y', 'Wind Deviation_z', 'Error'])
                with open("./build/px4_sitl_default/tmp/rootfs/log/error_log.csv", "a") as f:
                    df.to_csv(f, encoding='utf-8', index=False, header=False)
                
                # kill px4, jmavsim, and mission
                px4.kill()
                mission.kill()
                error = True
                break

    if error == False:
        os.system("python data_organize.py")

     

    # outs, errs = mission.communicate()
    # # mission.wait(90)
    # print(outs)
    # print(errs)
    # os.chdir("/Users/jeaniechen/Desktop/CMU_REU/Firmware")
    # print(out.stdout)

main()