import os
import time

def main():
     # testing
    #  print("hi from simulate.py")
    os.system("open -a QGroundControl")    # for automatic logging
    os.chdir("/Users/jeaniechen/Desktop/CMU_REU/Firmware")
    os.system("make px4_sitl jmavsim")
    #os.system("open -a Terminal /Users/jeaniechen/Desktop/CMU_REU/missionapp")
    #time.sleep(20)
    #os.system("make")
    #os.system("./missionapp --enforcer=ElasticEnforcer udp://")

if __name__ == "__main__":
    main()