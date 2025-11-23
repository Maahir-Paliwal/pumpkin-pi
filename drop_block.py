from utils.brick import BP, Motor, wait_ready_sensors
import time
from utils import sound

FORWARD_ROTATION = 180 #180 deg/sec
MOTOR_ROTATION_TIME = 1
DROP_SOUND = sound.Sound(duration=0.5, pitch=400, volume=80)

MOTOR = Motor("A")

wait_ready_sensors()
print("delivery system started")

def drop_block():
    MOTOR.set_dps(FORWARD_ROTATION)
    time.sleep(MOTOR_ROTATION_TIME)
    MOTOR.set_dps(0)
    DROP_SOUND.play()
    DROP_SOUND.wait_done()


if __name__ == "__main__":
    drop_block()
    BP.reset_all()
