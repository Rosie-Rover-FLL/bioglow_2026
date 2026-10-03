from pybricks.messaging import BLERadio
from pybricks.parameters import Button
from pybricks.tools import Matrix, StopWatch, wait

import rosie_rover
from remote_protocol import (
    MAX_ARM_DUTY_PCT,
    MAX_DRIVE_SPEED_MMSEC,
    MAX_TILT_DEG,
    MODE_ATTACHMENT,
    MODE_DRIVE,
    REMOTE_BROADCAST_CHANNEL,
    ROBOT_BROADCAST_CHANNEL,
)

# Import mission modules here as they're written.
import m1
import m2
import m3
import m6
import m13

# Map mission numbers to their run functions. Add an entry here each time
# a new mission module is imported above. Never map mission 0 -- that
# number is reserved for remote control mode (see the main loop below).
MISSIONS = {
    1: m1.run,
    2: m2.run,
    3: m3.run,
    6: m6.run,
    13: m13.run,
}

MAX_TURN_RATE_DEGSEC = 200

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

(
    left_top_motor,
    right_top_motor,
    left_color_sensor,
    right_color_sensor,
    prime_hub,
    drive_base,
) = rosie_rover.setup()
radio = BLERadio(ROBOT_BROADCAST_CHANNEL, [REMOTE_BROADCAST_CHANNEL])

prime_hub.speaker.volume(10 if USE_LOW_VOLUME_BEEP else 100)
rosie_rover.print_battery(prime_hub)

# By default, pressing CENTER stops the program. We want CENTER to launch
# missions instead, so require CENTER+BLUETOOTH together to stop the program.
prime_hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

mission_number = 1


def wait_for_release():
    while prime_hub.buttons.pressed():
        wait(10)


def clamp(value, low, high):
    return max(low, min(high, value))


def stop_remote_motion():
    drive_base.stop()
    left_top_motor.dc(0)
    right_top_motor.dc(0)


def handle_remote():
    received = radio.observe(REMOTE_BROADCAST_CHANNEL)
    if received is None:
        stop_remote_motion()
        return

    mode, speed_pct, pitch, roll = received
    # Measured on real hardware: tipping forward gives negative pitch, and
    # tipping left gives positive roll -- both opposite of what drive_base
    # wants (positive speed = forward, positive turn_rate = clockwise/right).
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    tilt_side = clamp(-roll / MAX_TILT_DEG, -1, 1)
    power_limit = speed_pct / 100

    if mode == MODE_DRIVE:
        left_top_motor.dc(0)
        right_top_motor.dc(0)
        speed = MAX_DRIVE_SPEED_MMSEC * power_limit * tilt_forward
        turn_rate = MAX_TURN_RATE_DEGSEC * power_limit * tilt_side
        drive_base.drive(speed, turn_rate)

    elif mode == MODE_ATTACHMENT:
        drive_base.stop()
        arm_duty = MAX_ARM_DUTY_PCT * power_limit * tilt_forward
        left_top_motor.dc(arm_duty)
        right_top_motor.dc(arm_duty)


prime_hub.display.number(mission_number)

try:
    while True:
        # Mission 0 is reserved for remote control -- no CENTER press
        # needed, it's just active the whole time the display reads 0, and
        # completely ignored otherwise. This is so the remote's small
        # resting movements never nudge the robot while it's being placed
        # for a mission.
        if mission_number == 0:
            handle_remote()

        pressed = prime_hub.buttons.pressed()
        was_remote_active = mission_number == 0

        if Button.RIGHT in pressed:
            mission_number += 1
            if mission_number > 99:
                mission_number = 0
            prime_hub.display.number(mission_number)
            wait_for_release()

        elif Button.LEFT in pressed:
            mission_number -= 1
            if mission_number < 0:
                mission_number = 99
            prime_hub.display.number(mission_number)
            wait_for_release()

        elif Button.CENTER in pressed:
            wait_for_release()
            run_mission = MISSIONS.get(mission_number)
            if run_mission:
                rosie_rover.print_battery(prime_hub)
                print(f"Starting Mission {mission_number:02}")
                prime_hub.speaker.beep()
                prime_hub.display.icon(PLAY_ICON)
                watch = StopWatch()
                run_mission(
                    left_top_motor,
                    right_top_motor,
                    left_color_sensor,
                    right_color_sensor,
                    prime_hub,
                    drive_base,
                )
                elapsed_sec = watch.time() / 1000
                prime_hub.speaker.beep()
                print(f"Finished Mission {mission_number:02}, time {elapsed_sec:.1f} seconds")
            else:
                prime_hub.display.icon(CHECKER_A)
                wait(500)
                prime_hub.display.icon(CHECKER_B)
                wait(500)
                mission_number = max(MISSIONS)
            prime_hub.display.number(mission_number)

        if was_remote_active and mission_number != 0:
            stop_remote_motion()

        wait(10)
finally:
    # The stop button raises inside the loop rather than letting the
    # program finish normally, so nothing guarantees motors get stopped
    # unless we do it here ourselves.
    stop_remote_motion()
    print("Goodbye")
