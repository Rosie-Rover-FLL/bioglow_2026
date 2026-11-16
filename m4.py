from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Drive to the Lucky Leaves.
    drive_base.settings(straight_speed=500)
    drive_base.use_gyro(True)
    drive_base.straight(700)
    drive_base.arc(-120, angle=50)

    # Raise the arm with everything maxed out (same as m2): full speed
    # (1000 deg/s) and the firmware's highest start/stop acceleration
    # (20000 deg/s², default is 2000).
    left_top_motor.control.limits(acceleration=20000)
    right_top_motor.control.limits(acceleration=20000)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, 1000, 210)
    # Back to the default so other missions aren't affected.
    left_top_motor.control.limits(acceleration=2000)
    right_top_motor.control.limits(acceleration=2000)

    drive_base.arc(-150, angle=-60)
    drive_base.straight(-720)
