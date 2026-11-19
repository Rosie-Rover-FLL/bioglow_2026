def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Bump the m13 model so its trees fully raise.
    drive_base.use_gyro(True)
    drive_base.settings(straight_speed=800)
    drive_base.straight(300)
    drive_base.straight(-350)
