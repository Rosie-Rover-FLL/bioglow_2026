from rosie_rover import TEST_DELAY, straight_until_done_or_stalled
from pybricks.tools import wait

# How far to drive for the ant push (mm). Stops early if it stalls, so really this number is about 190 but boosted to 220
PUSH_DRIVE_MM = 220


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    drive_base.settings(straight_speed=500)
    drive_base.straight(550)
    drive_base.arc(23, angle=65)
    drive_base.straight(270)
    drive_base.turn(35)

    # Ant push
    drive_base.settings(straight_speed=70)
    push_start = drive_base.distance()
    straight_until_done_or_stalled(drive_base, PUSH_DRIVE_MM)
    pushed = drive_base.distance() - push_start
    print("Ant push mm:", pushed)

    # Back up to 85 mm past the push start, no matter how far the push got
    drive_base.settings(straight_speed=350)
    back_up = pushed - 85
    if back_up > 0:
        drive_base.straight(-back_up)
    drive_base.turn(96)

    # Hit the window
    straight_until_done_or_stalled(drive_base, 180)

    # Drive home
    drive_base.settings(straight_speed=400)
    drive_base.straight(-100)
    drive_base.turn(-65)
    drive_base.arc(230, angle=85)
    straight_until_done_or_stalled(drive_base, 500)
    drive_base.use_gyro(False)
