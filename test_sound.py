from utils import sound

from utils.brick import  wait_ready_sensors, TouchSensor, BP
import time


TOUCH_SENSOR_POLL = 0.05
tone1 = sound.Sound(duration=1.0, volume=80, pitch="A3")
TOUCH_SENSOR = TouchSensor(1)

wait_ready_sensors()

try:
    while True:
        if TOUCH_SENSOR.is_pressed():
            tone1.play()
            tone1.wait_done()
        time.sleep(TOUCH_SENSOR_POLL)
        

except Exception as e:
    pass

finally:
    BP.reset_all()





