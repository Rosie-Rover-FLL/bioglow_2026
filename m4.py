from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Drive to the Lucky Leaves.
    drive_base.settings(straight_speed=500)
    drive_base.use_gyro(True)
    drive_base.straight(700)
    drive_base.arc(-120, angle=50)

    # Raise the arm at max speed and acceleration.
    arm_until_done_or_stalled(left_top_motor, right_top_motor, 300, 200)

    drive_base.arc(-150, angle=-60)
    drive_base.straight(-720)
