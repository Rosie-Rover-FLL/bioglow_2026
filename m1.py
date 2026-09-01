import rosie_rover
from pybricks.tools import wait

def run(robot):
    # robot.drive_base.straight(170)
    # robot.drive_base.turn(90)
    # robot.drive_base.straight(150)

    robot.drive_base.straight(-700)
    robot.drive_base.straight(250)
    robot.drive_base.settings(straight_speed=100)
    robot.drive_base.straight(700)
    wait(1000)
    robot.drive_base.turn(45)
    wait(500)
    robot.drive_base.straight(-40)
    robot.drive_base.turn(25)
    wait(1000)
    robot.drive_base.straight(180)


if __name__ == "__main__":
    robot = rosie_rover.RosieRover()
    run(robot)
