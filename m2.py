from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Fake demo mission: go out, lift up, lift down, go back.

    drive_base.drive(200, 0)
    wait(2000)
    drive_base.stop()

    left_top_motor.run_angle(200, 180, wait=False)
    right_top_motor.run_angle(200, 180)

    left_top_motor.run_angle(200, -180, wait=False)
    right_top_motor.run_angle(200, -180)

    drive_base.drive(-200, 0)
    wait(2000)
    drive_base.stop()
