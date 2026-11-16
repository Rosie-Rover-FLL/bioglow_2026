from rosie_rover import TEST_DELAY, straight_until_done_or_stalled
from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    # Sets the rover speed fast initially
    drive_base.settings(straight_speed=500)
    drive_base.straight(550)
    drive_base.arc(23, angle=65)
    drive_base.straight(270)
    drive_base.turn(35)

    # Ant push
    drive_base.settings(straight_speed=85)
    straight_until_done_or_stalled(drive_base, 270)

    # Back away and window prep
    drive_base.settings(straight_speed=350)
    drive_base.straight(-110)
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
