#!/usr/bin/env python3

"""
This test is used to collect data from the color sensor.
It must be run on the robot.
"""

# Add your imports here, if any
from utils.brick import EV3ColorSensor, wait_ready_sensors, reset_brick
import time

COLOR_SENSOR_DATA_FILE = "./data_analysis/color_sensor_black_luminescence.csv"
SENSOR_POLL_SLEEP = 0.05

# complete this based on your hardware setup
COLOR_SENSOR = EV3ColorSensor(3)

wait_ready_sensors(True) # Input True to see what the robot is trying to initialize! False to be silent.
print("color sensors ready to test")

def collect_color_sensor_data():
    "Collect color sensor data."
    ...
    try:
        output_file = open(COLOR_SENSOR_DATA_FILE, "w")

        while True:
            data = COLOR_SENSOR.get_value()
            if data != None:
                (red, gre, blu, lum) = data
                output_file.write(str([lum]) + "\n")
                print("Ready to collect again")
            else:
                print("Value not recorded, try again")
            
            time.sleep(SENSOR_POLL_SLEEP)
                
        
    except BaseException as error:
        # CTRL C
        print(error)
        pass
    finally:
        print("we are in finally")
        reset_brick()
        output_file.close()
        exit()


if __name__ == "__main__":
    collect_color_sensor_data()
