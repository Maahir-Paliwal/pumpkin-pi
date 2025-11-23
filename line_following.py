from utils.brick import BP, Motor, wait_ready_sensors, SensorError, EV3ColorSensor
import time


FORWARD_SPEED = 35
SENSOR_POLL_SLEEP = 0.02

MAX_DPS = 720

LEFT_MOTOR = Motor("C")
RIGHT_MOTOR = Motor("B")
C_SENSOR = EV3ColorSensor(3)

TURN_FACTOR = 1.5

wait_ready_sensors()
print("locomotion system starting")

BLACK_LUM = 650
WHITE_LUM = 690
threshold = (BLACK_LUM + WHITE_LUM) / 2


def follow_the_line(stop_event):
    try:
        while not stop_event.is_set():
            try:
                red, green, blue, lum = C_SENSOR.get_value()
            except SensorError as error:
                print(error)
                time.sleep(SENSOR_POLL_SLEEP)
                continue

            error = lum - threshold
            turn = TURN_FACTOR * error

            left_pct = FORWARD_SPEED + turn
            right_pct = FORWARD_SPEED - turn

            left_pct = max(-100, min(left_pct, 100))
            right_pct = max(-100, min(right_pct, 100))

            left_dps = (left_pct / 100.0) * MAX_DPS
            right_dps = (right_pct / 100.0) * MAX_DPS

            LEFT_MOTOR.set_dps(left_dps)
            RIGHT_MOTOR.set_dps(right_dps)

            time.sleep(SENSOR_POLL_SLEEP)

    except KeyboardInterrupt:
        print("Stopping...")
        LEFT_MOTOR.set_dps(0)
        RIGHT_MOTOR.set_dps(0)
        BP.reset_all()

    finally:
        LEFT_MOTOR.set_dps(0)
        RIGHT_MOTOR.set_dps(0)