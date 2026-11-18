from pybricks.tools import wait

def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    drive_base.settings(
        straight_speed=200,
        straight_acceleration=(300, 300)
    )

    # creature in box 1/2 from
    drive_base.straight(225)
    left_top_motor.dc(-100)
    right_top_motor.dc(-100)
    wait(400)
    left_top_motor.stop()
    right_top_motor.stop()
    # Fast return: near max speed (742), Pybricks default acceleration
    drive_base.settings(
        straight_speed=700,
        straight_acceleration=(1113, 1113)
    )
    drive_base.straight(-250)