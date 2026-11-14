from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Gyro on for this mission (reset to off before every mission).
    drive_base.use_gyro(True)
    drive_base.settings(straight_speed=800)
    drive_base.straight(-600)
    drive_base.straight(680)
