import rosie_rover
from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Fake demo mission: go out, lift up, lift down, go back.

    drive_base.drive(200, 0)
    wait(2000)
    drive_base.stop()

    left_top_motor.dc(50)
    right_top_motor.dc(50)
    wait(1000)
    left_top_motor.dc(0)
    right_top_motor.dc(0)

    left_top_motor.dc(-50)
    right_top_motor.dc(-50)
    wait(1000)
    left_top_motor.dc(0)
    right_top_motor.dc(0)

    drive_base.drive(-200, 0)
    wait(2000)
    drive_base.stop()


if __name__ == "__main__":
    run(*rosie_rover.setup())
