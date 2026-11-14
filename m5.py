from rosie_rover import TEST_DELAY, straight_until_done_or_stalled
from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Gyro on for this mission (reset to off before every mission).
    drive_base.use_gyro(True)
    wait(TEST_DELAY)
    drive_base.straight(760)
    wait(TEST_DELAY)
    left_top_motor.dc(100)
    right_top_motor.dc(100)
    wait(150)
    right_top_motor.brake()
    left_top_motor.brake()
    drive_base.straight(-165)
    wait(TEST_DELAY)
    drive_base.turn(25)
    wait(TEST_DELAY)
    drive_base.straight(-600)
