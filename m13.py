from pybricks.tools import wait

def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Gyro on for this mission (reset to off before every mission).
    drive_base.use_gyro(True)
    drive_base.settings(straight_speed=300)

    # creature in box 1/2 from
    drive_base.straight(225)
    left_top_motor.dc(-100)
    right_top_motor.dc(-100)
    wait(400)
    left_top_motor.stop()
    right_top_motor.stop()
    drive_base.settings(straight_speed=600)
    drive_base.straight(-250)