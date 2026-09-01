from pybricks.parameters import Button
from pybricks.tools import Matrix, StopWatch, wait

import rosie_rover
from remote_protocol import (
    LOCK_LEFT,
    LOCK_RIGHT,
    MAX_TILT_DEG,
    MODE_ATTACHMENT,
    MODE_DRIVE,
    REMOTE_BROADCAST_CHANNEL,
)

# Import mission modules here as they're written.
import m1
import m2

# Map mission numbers to their run functions. Add an entry here each time
# a new mission module is imported above.
MISSIONS = {
    1: m1.run,
    2: m2.run,
}

# Set to False before competition day to ignore the remote entirely.
IS_REMOTE_ENABLED = True

MAX_DRIVE_SPEED_MMSEC = 500
MAX_TURN_RATE_DEGSEC = 200
MAX_ARM_DUTY_PCT = 70

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

# Right-pointing "play" triangle, shown on the display while a mission runs.
PLAY_ICON = Matrix(
    [
        [0, 100, 0, 0, 0],
        [0, 100, 100, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 100, 0, 0],
        [0, 100, 0, 0, 0],
    ]
)

# Set to False for full volume; True for late-night/quiet testing.
USE_LOW_VOLUME_BEEP = True

ROSIE_ROVER_BANNER = r"""
 ___  ___  ___ ___ ___   ___  _____   _____ ___
| _ \/ _ \/ __|_ _| __| | _ \/ _ \ \ / / __| _ \
|   / (_) \__ \| || _|  |   / (_) \ V /| _||   /
|_|_\\___/|___/___|___| |_|_\\___/ \_/ |___|_|_\
"""

print(ROSIE_ROVER_BANNER)

robot = rosie_rover.RosieRover()
hub = robot.prime_hub
hub.speaker.volume(10 if USE_LOW_VOLUME_BEEP else 100)
robot.print_battery()

# By default, pressing CENTER stops the program. We want CENTER to launch
# missions instead, so require CENTER+BLUETOOTH together to stop the program.
hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

mission_number = 1


def wait_for_release():
    while hub.buttons.pressed():
        wait(10)


def clamp(value, low, high):
    return max(low, min(high, value))


def handle_remote():
    received = robot.radio.observe(REMOTE_BROADCAST_CHANNEL)
    if received is None:
        robot.drive_base.stop()
        robot.left_top.dc(0)
        robot.right_top.dc(0)
        return

    mode, speed_pct, pitch, roll, lock = received
    # Measured on real hardware: tipping forward gives negative pitch, and
    # tipping left gives positive roll -- both opposite of what drive_base
    # wants (positive speed = forward, positive turn_rate = clockwise/right).
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    tilt_side = clamp(-roll / MAX_TILT_DEG, -1, 1)
    power_limit = speed_pct / 100

    if mode == MODE_DRIVE:
        robot.left_top.dc(0)
        robot.right_top.dc(0)
        speed = MAX_DRIVE_SPEED_MMSEC * power_limit * tilt_forward
        turn_rate = MAX_TURN_RATE_DEGSEC * power_limit * tilt_side
        robot.drive_base.drive(speed, turn_rate)

    elif mode == MODE_ATTACHMENT:
        robot.drive_base.stop()
        arm_duty = MAX_ARM_DUTY_PCT * power_limit * tilt_forward
        robot.left_top.dc(0 if lock == LOCK_LEFT else arm_duty)
        robot.right_top.dc(0 if lock == LOCK_RIGHT else arm_duty)


hub.display.number(mission_number)

try:
    while True:
        if IS_REMOTE_ENABLED:
            handle_remote()

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
                print(f"Starting Mission {mission_number:02}")
                hub.speaker.beep()
                hub.display.icon(PLAY_ICON)
                watch = StopWatch()
                run_mission(robot)
                elapsed_sec = watch.time() / 1000
                hub.speaker.beep()
                print(f"Finished Mission {mission_number:02}, time {elapsed_sec:.1f} seconds")
            else:
                hub.display.icon(CHECKER_A)
                wait(500)
                hub.display.icon(CHECKER_B)
                wait(500)
                mission_number = max(MISSIONS)
            hub.display.number(mission_number)

        wait(10)
finally:
    print("Goodbye")
