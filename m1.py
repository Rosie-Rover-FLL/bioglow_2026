import rosie_rover
from pybricks.tools import wait

def run(robot):
    robot.drive_base.settings(straight_speed=800)
    robot.drive_base.straight(-550)
    robot.drive_base.straight(550)


if __name__ == "__main__":
    robot = rosie_rover.RosieRover()
    run(robot)
