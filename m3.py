import rosie_rover
from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=800)
    drive_base.straight(-400)
    drive_base.straight(345)
    # drive_base.settings(straight_speed=800)
    # drive_base.straight(700)
    # wait(1000)
    # drive_base.turn(45)
    # wait(500)
    # drive_base.straight(-40)
    # drive_base.turn(25)
    # wait(1000)
    # drive_base.straight(180)

    # Fake demo mission: like m2, but the arm phases are split around the
    # return trip instead of both happening before it, reversed (down
    # first, then up), slower, and shorter.

    # drive_base.drive(200, 0)
    # wait(2000)
    # drive_base.stop()

    # left_top_motor.dc(-35)
    # right_top_motor.dc(-35)
    # wait(500)
    # left_top_motor.dc(0)
    # right_top_motor.dc(0)

    # drive_base.drive(-200, 0)
    # wait(2000)
    # drive_base.stop()

    # left_top_motor.dc(35)
    # right_top_motor.dc(35)
    # wait(500)
    # left_top_motor.dc(0)
    # right_top_motor.dc(0)


if __name__ == "__main__":
    run(*rosie_rover.setup())
