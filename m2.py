from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=450)
    drive_base.straight(265)

    arm_until_done_or_stalled(left_top_motor, right_top_motor, 200, 180)

    drive_base.straight(-350)
