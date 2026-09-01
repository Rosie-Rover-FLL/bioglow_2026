from pybricks.parameters import Button
from pybricks.tools import Matrix, wait

import rosie_rover

# Import mission modules here as they're written.
import m1

# Map mission numbers to their run functions. Add an entry here each time
# a new mission module is imported above.
MISSIONS = {
    1: m1.run,
}

# Opposite checkerboard patterns, flashed when CENTER is pressed on a number
# with no mission mapped to it.
CHECKER_A = Matrix(
    [
        [100, 0, 100, 0, 100],
        [0, 100, 0, 100, 0],
        [100, 0, 100, 0, 100],
        [0, 100, 0, 100, 0],
        [100, 0, 100, 0, 100],
    ]
)
CHECKER_B = Matrix(
    [
        [0, 100, 0, 100, 0],
        [100, 0, 100, 0, 100],
        [0, 100, 0, 100, 0],
        [100, 0, 100, 0, 100],
        [0, 100, 0, 100, 0],
    ]
)

robot = rosie_rover.RosieRover()
hub = robot.prime_hub
robot.print_battery()

# By default, pressing CENTER stops the program. We want CENTER to launch
# missions instead, so require CENTER+BLUETOOTH together to stop the program.
hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

mission_number = 1


def wait_for_release():
    while hub.buttons.pressed():
        wait(10)


hub.display.number(mission_number)

while True:
    pressed = hub.buttons.pressed()

    if Button.RIGHT in pressed:
        mission_number += 1
        if mission_number > 99:
            mission_number = 1
        hub.display.number(mission_number)
        wait_for_release()

    elif Button.LEFT in pressed:
        mission_number -= 1
        if mission_number < 1:
            mission_number = 99
        hub.display.number(mission_number)
        wait_for_release()

    elif Button.CENTER in pressed:
        wait_for_release()
        run_mission = MISSIONS.get(mission_number)
        if run_mission:
            robot.print_battery()
            run_mission(robot)
        else:
            hub.display.icon(CHECKER_A)
            wait(500)
            hub.display.icon(CHECKER_B)
            wait(500)
            mission_number = max(MISSIONS)
        hub.display.number(mission_number)

    wait(10)
