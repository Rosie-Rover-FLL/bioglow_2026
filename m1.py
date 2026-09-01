import rosie_rover


def run(robot):
    robot.drive_base.straight(170)
    robot.drive_base.turn(90)
    robot.drive_base.straight(150)


if __name__ == "__main__":
    robot = rosie_rover.RosieRover()
    run(robot)
