from rosie_rover import straight_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Bump the m13 model so its trees fully raise.
    drive_base.use_gyro(True)
    drive_base.settings(straight_speed=800, straight_acceleration=(5000, 5000))
    # Aims past the model so it hits at full speed, then stops on the stall.
    straight_until_done_or_stalled(drive_base, 400)
    drive_base.straight(-350)
