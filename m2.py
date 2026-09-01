import rosie_rover
from pybricks.tools import wait


def run(robot):
    # Fake demo mission: go out, lift up, lift down, go back.

    robot.drive_base.drive(200, 0)
    wait(2000)
    robot.drive_base.stop()

    robot.left_top_motor.dc(50)
    robot.right_top_motor.dc(50)
    wait(1000)
    robot.left_top_motor.dc(0)
    robot.right_top_motor.dc(0)

    robot.left_top_motor.dc(-50)
    robot.right_top_motor.dc(-50)
    wait(1000)
    robot.left_top_motor.dc(0)
    robot.right_top_motor.dc(0)

    robot.drive_base.drive(-200, 0)
    wait(2000)
    robot.drive_base.stop()


if __name__ == "__main__":
    robot = rosie_rover.RosieRover()
    run(robot)
