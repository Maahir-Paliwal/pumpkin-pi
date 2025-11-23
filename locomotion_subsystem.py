import threading
from utils.brick import EV3UltrasonicSensor, wait_ready_sensors, BP
from line_following import LEFT_MOTOR, RIGHT_MOTOR, C_SENSOR
import time
from datetime import datetime, timedelta

from line_following import follow_the_line
from office_navigation import enter_and_sweep_office, turn_degrees

DELAY_SEC = 0.01
US_SENSOR = EV3UltrasonicSensor(2)
DISTANCE_THRESHOLD = 8.9
OFFICE_TOLERANCE = 2

TOP_LEFT_OFFICE_DISTANCE = 81.5
TOP_RIGHT_OFFICE_DISTANCE = 82.4
BOTTOM_RIGHT_OFFICE_DISTANCE = 82.3
BOTTOM_LEFT_OFFICE_DISTANCE = 33.5

MAIL_ROOM_DISTANCE = 58.8

OFFICE_DOORS_BY_SIDE = {
    0: [],
    1: [TOP_LEFT_OFFICE_DISTANCE],
    2: [TOP_RIGHT_OFFICE_DISTANCE],
    3: [BOTTOM_RIGHT_OFFICE_DISTANCE, BOTTOM_LEFT_OFFICE_DISTANCE],
    4: [],
}

wait_ready_sensors()
print("ready to trace the whole square.")

starting_time = datetime.now()


# MOTION HELPER
def turn_right_90() -> None:
    """
    Turn right 90 degrees using the encoder
    """
    print("Turning right 90° at corner")

    turn_degrees(-90)


def trace_the_black_square():
    for side in range(4):
        print(f"starting side: {side}")

        doors_for_side = OFFICE_DOORS_BY_SIDE.get(side, [])
        next_door_index = 0

        stop_event = threading.Event()
        line_follow_thread = threading.Thread(
            target=follow_the_line,
            args=(stop_event,),
            daemon=True,
        )
        # trace one side
        line_follow_thread.start()

        try:
            while True:
                try:
                    distance = US_SENSOR.get_value()
                except Exception as e:
                    print(e)
                    time.sleep(DELAY_SEC)  # for constant polling
                    continue

                # ignore initial readings
                if (datetime.now() - timedelta(seconds=3)) < starting_time:
                    time.sleep(DELAY_SEC)
                    print(f"skipping this one: {distance}")
                    continue

                # Handle office doors for this side
                if next_door_index < len(doors_for_side):
                    target_dist = doors_for_side[next_door_index]
                    # Only trigger once we are at or just past the door
                    if target_dist - OFFICE_TOLERANCE <= distance <= target_dist:
                        print(f"Office door #{next_door_index} on side {side}")
                        print(f"Detected at distance: {distance:.1f}")

                        stop_event.set()
                        line_follow_thread.join()

                        delivered = enter_and_sweep_office(turn_direction="right")
                        print(f"Office #{next_door_index} on side {side}.")
                        print(f"{'DELIVERED' if delivered else 'NO DELIVERY'}.")

                        next_door_index += 1

                        # resume line following on this side
                        stop_event = threading.Event()
                        line_follow_thread = threading.Thread(
                            target=follow_the_line,
                            args=(stop_event,),
                            daemon=True,
                        )
                        line_follow_thread.start()

                # Corner detection
                if distance <= DISTANCE_THRESHOLD:
                    print(f"Corner detected on side: {side} at distance: {distance:.1f}")
                    break

                time.sleep(DELAY_SEC)

        except KeyboardInterrupt:
            print("Interrupted from keyboard.")
            stop_event.set()
            line_follow_thread.join()
            BP.reset_all()
            return

        # stop the thread and wait
        stop_event.set()
        line_follow_thread.join()

        print(f"Turning right at the end of side: {side}")
        turn_right_90()


    BP.reset_all()
    print("Done.")


if __name__ == "__main__":
    trace_the_black_square()