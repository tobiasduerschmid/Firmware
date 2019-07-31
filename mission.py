import os


def main():
     # testing
    #os.system("open -a Terminal /Users/jeaniechen/Desktop/CMU_REU/missionapp")
    #time.sleep(20)
    os.chdir("/Users/jeaniechen/Desktop/CMU_REU/missionapp")
    os.system("make")
    os.system("./missionapp --enforcer=ElasticEnforcer udp://")
    os.chdir("/Users/jeaniechen/Desktop/CMU_REU/Firmware")


if __name__ == "__main__":
    main()