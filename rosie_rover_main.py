from pybricks.messaging import BLERadio
from pybricks.parameters import Button, Icon
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

import m1
import m2
import m3
import m4
import m5
import m6
import m7
import m9
import m13
import m15
import m16
import m17

# Never map mission 0 -- it's remote control.
MISSIONS = {
    1: m1.run,
    2: m2.run,
    3: m3.run,
    4: m4.run,
    5: m5.run,
    6: m6.run,
    7: m7.run,
    9: m9.run,
    13: m13.run,
    15: m15.run,
    16: m16.run,
    17: m17.run,
}

MAX_MISSION = 17

MAX_TURN_RATE_DEGSEC = 200

# Flashed when CENTER is pressed on a number with no mission.
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

# Shown while a mission runs.
PLAY_ICON = Matrix(
    [
        [0, 100, 0, 0, 0],
        [0, 100, 100, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 100, 0, 0],
        [0, 100, 0, 0, 0],
    ]
)

# Missions that show an icon instead of their number.
MISSION_ICONS = {
    17: Icon.ARROW_UP,
}

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

# CENTER launches missions, so CENTER+BLUETOOTH stops the program.
prime_hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

# Show "C" while the gyro calibrates (keep the robot still).
# At least 1.5 s, up to 5 s if the gyro isn't ready.
prime_hub.display.char("C")
calibration_watch = StopWatch()
while calibration_watch.time() < 1500 or not prime_hub.imu.ready():
    if calibration_watch.time() > 5000:
        print("Gyro not calibrated yet -- set the robot down and keep it still.")
        break
    wait(10)

mission_number = 1


def show_mission(number):
    icon = MISSION_ICONS.get(number)
    if icon:
        prime_hub.display.icon(icon)
    else:
        prime_hub.display.number(number)


def wait_for_release():
    while prime_hub.buttons.pressed():
        wait(10)


def clamp(value, low, high):
    return max(low, min(high, value))


wheels_held = False

# Last remote message acted on, so repeats are ignored.
last_message = None


def hold_wheels():
    # Locks the wheels (stop() only coasts). Only once per hold:
    # each hold() re-targets to the current spot, so repeating it lets them creep.
    global wheels_held
    if not wheels_held:
        drive_base.hold()
        wheels_held = True


def stop_remote_motion():
    global wheels_held, last_message
    drive_base.stop()
    wheels_held = False
    last_message = None
    left_top_motor.dc(0)
    right_top_motor.dc(0)


def handle_remote():
    global wheels_held, last_message
    received = radio.observe(REMOTE_BROADCAST_CHANNEL)
    if received == last_message:
        return  # nothing new (also covers "still no signal")
    if received is None:
        # Signal just lost -- stop once.
        stop_remote_motion()
        return
    last_message = received

    mode, speed_pct, pitch, roll = received
    # Pitch and roll are both backwards from what drive_base wants (measured on hardware).
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    tilt_side = clamp(-roll / MAX_TILT_DEG, -1, 1)
    power_limit = speed_pct / 100

    if mode == MODE_DRIVE:
        wheels_held = False
        left_top_motor.dc(0)
        right_top_motor.dc(0)
        speed = MAX_DRIVE_SPEED_MMSEC * power_limit * tilt_forward
        turn_rate = MAX_TURN_RATE_DEGSEC * power_limit * tilt_side
        drive_base.drive(speed, turn_rate)

    elif mode == MODE_ATTACHMENT:
        hold_wheels()
        arm_duty = MAX_ARM_DUTY_PCT * power_limit * tilt_forward
        left_top_motor.dc(arm_duty)
        right_top_motor.dc(arm_duty)

    else:  # MODE_LOCKED (or anything unknown): nothing moves
        hold_wheels()
        left_top_motor.dc(0)
        right_top_motor.dc(0)


def launch_mission(number):
    # Returns True if the mission finished, False if CENTER aborted it.
    rosie_rover.reset_drive_settings(drive_base)
    rosie_rover.reset_arm_settings(left_top_motor, right_top_motor)
    rosie_rover.print_battery(prime_hub)
    print(f"Starting Mission {number:02}")
    prime_hub.speaker.beep()
    prime_hub.display.icon(PLAY_ICON)
    watch = StopWatch()
    # During a mission, CENTER aborts it and returns to the menu.
    prime_hub.system.set_stop_button(Button.CENTER)
    aborted = False
    try:
        MISSIONS[number](
            left_top_motor,
            right_top_motor,
            left_color_sensor,
            right_color_sensor,
            prime_hub,
            drive_base,
        )
    except SystemExit:
        aborted = True
    finally:
        prime_hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))
    # Release the final Stop.HOLD, and stop anything still moving after an abort.
    stop_remote_motion()
    # Remote control always drives gyro-off.
    drive_base.use_gyro(False)
    elapsed_sec = watch.time() / 1000
    prime_hub.speaker.beep()
    if aborted:
        print(f"Aborted Mission {number:02}, time {elapsed_sec:.1f} seconds")
        # Don't relaunch from the CENTER press that aborted.
        wait_for_release()
        return False
    print(f"Finished Mission {number:02}, time {elapsed_sec:.1f} seconds")
    return True


show_mission(mission_number)

try:
    while True:
        # Remote control is active only while the display reads 0.
        if mission_number == 0:
            handle_remote()

        pressed = prime_hub.buttons.pressed()
        was_remote_active = mission_number == 0

        if Button.RIGHT in pressed:
            mission_number += 1
            if mission_number > MAX_MISSION:
                mission_number = 0
            show_mission(mission_number)
            wait_for_release()

        elif Button.LEFT in pressed:
            mission_number -= 1
            if mission_number < 0:
                mission_number = MAX_MISSION
            show_mission(mission_number)
            wait_for_release()

        elif Button.CENTER in pressed:
            wait_for_release()
            if mission_number in MISSIONS:
                launch_mission(mission_number)
            else:
                prime_hub.display.icon(CHECKER_A)
                wait(500)
                prime_hub.display.icon(CHECKER_B)
                wait(500)
                mission_number = max(MISSIONS)
            show_mission(mission_number)

        if was_remote_active and mission_number != 0:
            stop_remote_motion()

        wait(10)
finally:
    # The stop button doesn't stop motors for us, so do it here.
    stop_remote_motion()
    print("Goodbye")
