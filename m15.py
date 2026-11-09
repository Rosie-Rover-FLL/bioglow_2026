def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=600)
    drive_base.straight(-500)
    drive_base.turn(90)
    drive_base.straight(-580)
    drive_base.straight(540)
    drive_base.turn(120)
    drive_base.straight(-500)
