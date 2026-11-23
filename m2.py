from pybricks.tools import wait
from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    # Gentle start to avoid wheel slip.
    drive_base.settings(straight_speed=450, straight_acceleration=(550, 800))
    drive_base.straight(300)

    # Raise the arm at max speed and acceleration.
    left_top_motor.control.limits(acceleration=20000)
    right_top_motor.control.limits(acceleration=20000)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, 1000, 210)
    # Back to the default acceleration.
    left_top_motor.control.limits(acceleration=2000)
    right_top_motor.control.limits(acceleration=2000)

    # Drive back while lowering the arm.
    drive_base.straight(-350, wait=False)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, -500, 180)
    while not drive_base.done():
        wait(10)
