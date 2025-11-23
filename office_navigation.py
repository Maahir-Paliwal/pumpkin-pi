from utils.brick import BP
from line_following import LEFT_MOTOR, RIGHT_MOTOR, C_SENSOR
from line_following import FORWARD_SPEED, SENSOR_POLL_SLEEP as COLOUR_SENSOR_SLEEP_POLL, TURN_FACTOR, threshold, MAX_DPS
import time
from typing import Tuple

# for block dropping 
from drop_block import drop_block
import math

# ------ ROBOT GEOMETRY ------
WHEEL_DIAMETER_CM = 4.0
BASE_DIAMETER_CM = 13.0
WHEEL_CIRCUMFERENCE_CM = math.pi * WHEEL_DIAMETER_CM

DEGREES_PER_CM = 360.0 / WHEEL_CIRCUMFERENCE_CM

INPLACE_DEG_PER_ROBOT_DEG = BASE_DIAMETER_CM / WHEEL_DIAMETER_CM
PIVOT_DEG_PER_ROBOT_DEG   = 2 * BASE_DIAMETER_CM / WHEEL_DIAMETER_CM

# ------ MOVEMENT CONSTANTS -----
MOVE_DPS  = 180
TURN_DPS  = 180
SWEEP_DPS = 180
TURN_CALIBRATION = 1
FORWARD_DIST_AFTER_PACKAGE_DETECT = -4

# ------ SWEEPING CONSTANTS ------
SWEEP_ROBOT_DEG_90 = 90.0
PIVOT_WHEEL_DEG_90 = SWEEP_ROBOT_DEG_90 * PIVOT_DEG_PER_ROBOT_DEG


SWEEP_STEPS   = 3
STEP_DISTANCE_CM = 1.5
PRE_SWEEP_CM  = 0
MAX_DOOR_SEARCH_CM = 15.0

COLOUR_EUCLIDEAN_DISTANCE_THRESHOLD = 0.1


###COLOUR_SENSOR_SLEEP_POLL = 0.05




# ----------------- COLOUR ------------------
# COLOUR HELPER
def read_colour() -> Tuple[int, int, int,int]:
    '''
    return (R,G,B,LUM) for color sensor
    '''
    return C_SENSOR.get_value()

# COLOUR HELPER
def is_red(r:int, g:int, b:int) -> bool:
    '''
    NORMALIZE AND COMPARE WITH THE TESTING FOR RED
    '''
    total = r + g + b 
    if total == 0:
        return False
    
    r_norm = r/(r + g + b)
    g_norm = g/(r + g + b)
    b_norm = b/(r + g + b)
    return math.sqrt((r_norm - 0.79)**2 + (g_norm - 0.14)**2 + (b_norm - 0.07)**2) < COLOUR_EUCLIDEAN_DISTANCE_THRESHOLD

# COLOUR HELPER
def is_green(r:int, g:int, b:int) -> bool:
    '''
    NORMALIZE AND COMPARE WITH THE TESTING FOR GREEN
    '''
    total = r + g + b 
    if total == 0:
        return False

    r_norm = r/(r + g + b)
    g_norm = g/(r + g + b)
    b_norm = b/(r + g + b)

    return math.sqrt((r_norm - 0.36)**2 + (g_norm - 0.57)**2 + (b_norm - 0.07)**2) < COLOUR_EUCLIDEAN_DISTANCE_THRESHOLD
# ------------------------------------------


# ----------------- MOVEMENT ------------------

# MOVEMENT HELPER
def move_forward(cm: float, dps: int = MOVE_DPS) -> None:
    '''
    Move forward if cm > 0, move backward if cm < 0
    '''
    target_deg = abs(cm) * DEGREES_PER_CM
    direction = 1 if cm >= 0 else -1

    LEFT_MOTOR.reset_position()
    RIGHT_MOTOR.reset_position()

    LEFT_MOTOR.set_dps(direction * dps)
    RIGHT_MOTOR.set_dps(direction * dps)

    while True:
        left_pos  = abs(LEFT_MOTOR.get_position())
        right_pos = abs(RIGHT_MOTOR.get_position())
        avg_pos   = (left_pos + right_pos) / 2.0

        if avg_pos >= target_deg:
            break

        time.sleep(0.01)

    LEFT_MOTOR.set_dps(0)
    RIGHT_MOTOR.set_dps(0)






# MOVEMENT HELPER
def turn_degrees(angle: float, dps: int = TURN_DPS) -> None:
    """
    In-place rotation.

    angle > 0  → turn left
    angle < 0  → turn right
    """
    target_wheel_deg = abs(angle) * INPLACE_DEG_PER_ROBOT_DEG * TURN_CALIBRATION  # 4° wheel / 1° robot

    LEFT_MOTOR.reset_position()
    RIGHT_MOTOR.reset_position()

    if angle > 0: 
        LEFT_MOTOR.set_dps(-dps)
        RIGHT_MOTOR.set_dps(dps)
    else:          
        LEFT_MOTOR.set_dps(dps)
        RIGHT_MOTOR.set_dps(-dps)

    while True:
        left_pos  = abs(LEFT_MOTOR.get_position())
        right_pos = abs(RIGHT_MOTOR.get_position())
        avg_pos   = (left_pos + right_pos) / 2.0

        if avg_pos >= target_wheel_deg:
            break

        time.sleep(0.01)

    LEFT_MOTOR.set_dps(0)
    RIGHT_MOTOR.set_dps(0)




# MOVEMENT HELPER
def pivot_sweep_fixed_left() -> bool:
    """
    Sweep to the left around the left wheel by ~90° of robot rotation,
    scanning continuously for green. If green is seen, stop immediately,
    backtrack the same encoder distance, drop the block, and return True.
    """
    LEFT_MOTOR.set_dps(0)
    RIGHT_MOTOR.reset_position()
    RIGHT_MOTOR.set_dps(SWEEP_DPS)

    found = False
    pos_at_green = 0.0

    while True:
        pos = abs(RIGHT_MOTOR.get_position())
        if pos >= PIVOT_WHEEL_DEG_90:    # ≈720° wheel → 90° robot
            break

        data = read_colour()
        if data is not None:
            r, g, b, _ = data
            if is_green(r, g, b):
                found = True
                pos_at_green = pos
                break

        time.sleep(COLOUR_SENSOR_SLEEP_POLL)

    RIGHT_MOTOR.set_dps(0)

    if found:
        print("Green detected during left sweep arc.")
        move_forward(FORWARD_DIST_AFTER_PACKAGE_DETECT)
        drop_block()

        # back to centre: reverse by the same encoder amount
        RIGHT_MOTOR.reset_position()
        RIGHT_MOTOR.set_dps(-SWEEP_DPS)
        while abs(RIGHT_MOTOR.get_position()) < pos_at_green:
            time.sleep(0.01)
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)
        return True

    # no green: undo full 90° sweep to face forward again
    RIGHT_MOTOR.reset_position()
    RIGHT_MOTOR.set_dps(-SWEEP_DPS)
    while abs(RIGHT_MOTOR.get_position()) < PIVOT_WHEEL_DEG_90:
        time.sleep(0.01)
    RIGHT_MOTOR.set_dps(0)
    LEFT_MOTOR.set_dps(0)
    return False



# MOVEMENT HELPER
def pivot_sweep_fixed_right() -> bool:
    RIGHT_MOTOR.set_dps(0)
    LEFT_MOTOR.reset_position()
    LEFT_MOTOR.set_dps(SWEEP_DPS)

    found = False
    pos_at_green = 0.0

    while True:
        pos = abs(LEFT_MOTOR.get_position())
        if pos >= PIVOT_WHEEL_DEG_90:
            break

        data = read_colour()
        if data is not None:
            r, g, b, _ = data
            if is_green(r, g, b):
                found = True
                pos_at_green = pos
                break

        time.sleep(COLOUR_SENSOR_SLEEP_POLL)

    LEFT_MOTOR.set_dps(0)

    if found:
        print("Green detected during right sweep arc.")
        move_forward(FORWARD_DIST_AFTER_PACKAGE_DETECT)
        drop_block()

        LEFT_MOTOR.reset_position()
        LEFT_MOTOR.set_dps(-SWEEP_DPS)
        while abs(LEFT_MOTOR.get_position()) < pos_at_green:
            time.sleep(0.01)
        LEFT_MOTOR.set_dps(0)
        RIGHT_MOTOR.set_dps(0)
        return True

    # no green: undo full sweep
    LEFT_MOTOR.reset_position()
    LEFT_MOTOR.set_dps(-SWEEP_DPS)
    while abs(LEFT_MOTOR.get_position()) < PIVOT_WHEEL_DEG_90:
        time.sleep(0.01)
    LEFT_MOTOR.set_dps(0)
    RIGHT_MOTOR.set_dps(0)
    return False




# MOVEMENT HELPER
def sweep_step_for_green() -> bool:
    """
    One sweep step.

    1. Turn Left, if green is found, drop a block, realign to center, stop sweeping
    2. Turn Right, if green is found, drop a block, realign to center, stop sweeping
    3. If no green in either arc, face forward again and return False
    """

    # left sweep
    if pivot_sweep_fixed_left():
        return True
    

    # right sweep
    if pivot_sweep_fixed_right():
        return True
    
    return False




# MOVEMENT HELPER
def sweep_office_for_green() -> Tuple[bool, float]:
    """
    Perform the full 2cm step + sweep pattern when inside an office.

    Returns: (found_green, total_cm_forward)    
        found_green: True if green is found in the sweep
        total_cm_forward: how far forward we actually moved inside
    """

    total_cm_forward = 0

    for i in range(SWEEP_STEPS):
        print(f"Sweep {i + 1}/{SWEEP_STEPS} inside office.")
        
        move_forward(STEP_DISTANCE_CM)
        total_cm_forward += STEP_DISTANCE_CM
        
        if sweep_step_for_green():
            print("Green found while sweeping.")
            return True, total_cm_forward
        

    print("Finished sweep and no green was found.")
    return False, total_cm_forward


# MOVEMENT HELPER

def follow_line_into_office_until_door(max_distance_cm: float) -> Tuple[bool, float]:
    """
    Use line-following to go into the office along the black line,
    scanning for red.

    Returns: (found_red, travelled_cm)
        found_red: True if we saw red while following the line.
        travelled_cm: how far we moved forward along the line (in cm).
    """
    max_wheel_deg = max_distance_cm * DEGREES_PER_CM

    LEFT_MOTOR.reset_position()
    RIGHT_MOTOR.reset_position()

    while True:
        # --- how far have we gone along the line? ---
        left_pos  = abs(LEFT_MOTOR.get_position())
        right_pos = abs(RIGHT_MOTOR.get_position())
        avg_pos   = (left_pos + right_pos) / 2.0

        if avg_pos >= max_wheel_deg:
            # hit the maximum travel distance with no red
            LEFT_MOTOR.set_dps(0)
            RIGHT_MOTOR.set_dps(0)
            travelled_cm = avg_pos / DEGREES_PER_CM
            print(f"No red detected within {max_distance_cm} cm.")
            return False, travelled_cm

        # --- read colour + luminance ---
        data = read_colour()
        if data is None:
            time.sleep(COLOUR_SENSOR_SLEEP_POLL)
            continue

        r, g, b, lum = data

        # --- door check: red patch ---
        if is_red(r, g, b):
            print("Red detected while following line into office.")
            LEFT_MOTOR.set_dps(0)
            RIGHT_MOTOR.set_dps(0)
            travelled_cm = avg_pos / DEGREES_PER_CM
            return True, travelled_cm

        # --- DPS-based line-follow step (same logic as follow_the_line) ---
        error = lum - threshold
        turn = TURN_FACTOR * error

        # percentage “commands” around FORWARD_SPEED
        left_pct  = FORWARD_SPEED + turn
        right_pct = FORWARD_SPEED - turn

        # clamp to valid percent range
        left_pct  = max(-100, min(left_pct, 100))
        right_pct = max(-100, min(right_pct, 100))

        # convert to degrees per second
        left_dps  = (left_pct / 100.0) * MAX_DPS
        right_dps = (right_pct / 100.0) * MAX_DPS

        LEFT_MOTOR.set_dps(left_dps)
        RIGHT_MOTOR.set_dps(right_dps)

        time.sleep(COLOUR_SENSOR_SLEEP_POLL)

# ----------------------------------------------------------


def enter_and_sweep_office(turn_direction: str = "right") -> bool:
    """
    robot arrives at an office, turns right, and sweeps.

    returns:
        False if the robot did not deliver a package (robot could not enter office OR green square not found)
    """

    print(f"Attempting to enter the office, turn {turn_direction}")

    if turn_direction == "right":
        turn_degrees(-90)
    else:
        turn_degrees(90)


    found_red, travelled_cm = follow_line_into_office_until_door(MAX_DOOR_SEARCH_CM)

    if found_red:
        print(f"Red detected at the office door, I will not enter!")
        move_forward(-travelled_cm)

        # realign to be back on the outside border
        if turn_direction == "right":
            turn_degrees(90)
        else:
            turn_degrees(-90)
        return False

    print("No red at the door, entering the office!")

    # move a bit closer
    move_forward(PRE_SWEEP_CM)

    # sweep
    found_green, sweep_forward = sweep_office_for_green()

    # reverse the motion to return to the outer black box
    total_inside = travelled_cm + PRE_SWEEP_CM + sweep_forward
    move_forward(-total_inside - 3)

    if turn_direction == "right":
        turn_degrees(90)
    else:
        turn_degrees(-90)


    print(f"Returned to the outer black box after sweeping office.")
    return found_green
