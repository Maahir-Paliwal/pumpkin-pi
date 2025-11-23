from utils.brick import EV3UltrasonicSensor, wait_ready_sensors, BP

VAL1 = 0
VAL2 = 0
VAL3 = 0

def filter_distance(distance): 
    VAL1 = distance

    # redo reading if None
    if VAL1 is None: 
        return False
    
    #First reading 
    if VAL2 == 0 and distance != 0.0: 
        VAL2 = distance 

    if VAL3 == 0 and distance != 0.0: 
        VAL3 = distance


    # Once Val2, Val3 != 0
    avg = (VAL1 + VAL2 + VAL3) / 3

    # redo reading if the next reading is over the threshold
    if abs(VAL1 - avg) > 1: 
        return False
    
    # Update sliding windwos
    VAL3 = VAL2
    VAL2 = distance

    return True