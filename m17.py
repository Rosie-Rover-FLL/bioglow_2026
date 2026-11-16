from pybricks.parameters import Stop


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=700)  # near max (742), leaves the outer wheel room on the arc
    drive_base.use_gyro(True)
    drive_base.arc(-300, 78)
    drive_base.arc(-1400, 11)
    drive_base.turn(353)
    drive_base.arc(-4000, 15)
    drive_base.use_gyro(False)
