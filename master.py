from locomotion_subsystem import trace_the_black_square
from line_following import follow_the_line
from utils.brick import wait_ready_sensors, BP, TouchSensor
import time
from locomotion_subsystem import complete_all_deliveries 
import threading

T_SENSOR = TouchSensor(4)
TOUCH_SENSOR_POLL_SLEEP = 0.05



def emergency_stop():
    while True:
        try:
            if T_SENSOR.is_pressed():
                print("EMERGENCY STOP PRESSED -- GOODBYE!")
                BP.reset_all()
                raise SystemExit

        except Exception as e:
            print(e)
        
        time.sleep(TOUCH_SENSOR_POLL_SLEEP)



def main():

    emergency_stop_thread = threading.Thread(target=emergency_stop, daemon=True)
    emergency_stop_thread.start()
    
    try:
        complete_all_deliveries()
    except SystemExit:
        print("Emergency stop activated.")
    except KeyboardInterrupt:
        print("Keyboard interrupt, restarting program.")
    finally:
        BP.reset_all()

    
if __name__ == "__main__":
    main()





    




