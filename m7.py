from rosie_rover import (
    ARM_SLOP_DEGREES,
    ARM_SPEED_MEDIUM,
    TEST_DELAY,
    move_arm_degrees,
)
from pybricks.tools import wait

M7_ARM_RAISE_DEGREES = 20


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    # Start the arm at the bottom. Lift it, then drive.
    move_arm_degrees(left_top_motor, right_top_motor, M7_ARM_RAISE_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_MEDIUM)
    drive_base.straight(735)
    wait(TEST_DELAY)
    drive_base.turn(-27)
    wait(TEST_DELAY)
    left_top_motor.control.limits(acceleration=20000)
    right_top_motor.control.limits(acceleration=20000)

    left_top_motor.dc(100)
    right_top_motor.dc(100)

    left_top_motor.control.limits(acceleration=2000)
    right_top_motor.control.limits(acceleration=2000)
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
