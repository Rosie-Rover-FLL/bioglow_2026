import rosie_rover
from pybricks.tools import wait


def run(robot):
    # Fake demo mission: like m2, but the arm phases are split around the
    # return trip instead of both happening before it, reversed (down
    # first, then up), slower, and shorter.

    robot.drive_base.drive(200, 0)
    wait(2000)
    robot.drive_base.stop()

    robot.left_top_motor.dc(-35)
    robot.right_top_motor.dc(-35)
    wait(500)
    robot.left_top_motor.dc(0)
    robot.right_top_motor.dc(0)

    robot.drive_base.drive(-200, 0)
    wait(2000)
    robot.drive_base.stop()

    robot.left_top_motor.dc(35)
    robot.right_top_motor.dc(35)
    wait(500)
    robot.left_top_motor.dc(0)
    robot.right_top_motor.dc(0)


if __name__ == "__main__":
    robot = rosie_rover.RosieRover()
    run(robot)
