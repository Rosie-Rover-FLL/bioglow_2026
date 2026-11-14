from rosie_rover import TEST_DELAY, straight_until_done_or_stalled
from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.straight(735)
    wait(TEST_DELAY)
    drive_base.turn(-24)
    wait(TEST_DELAY)
    left_top_motor.dc(100)
    right_top_motor.dc(100)
    wait(150)
    left_top_motor.dc(-100)
    right_top_motor.dc(-100)
    wait(50)
    right_top_motor.brake()
    left_top_motor.brake()
    wait(TEST_DELAY)
    drive_base.turn(20)
    wait(TEST_DELAY)
    drive_base.straight(-735)
