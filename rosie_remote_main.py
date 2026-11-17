from pybricks.hubs import PrimeHub
from pybricks.messaging import BLERadio
from pybricks.parameters import Axis, Button, Port
from pybricks.pupdevices import Motor
from pybricks.tools import Matrix, StopWatch, wait

from remote_protocol import (
    MAX_ARM_DUTY_PCT,
    MAX_DRIVE_SPEED_MMSEC,
    MAX_TILT_DEG,
    MODE_ATTACHMENT,
    MODE_DRIVE,
    MODE_LOCKED,
    REMOTE_BROADCAST_CHANNEL,
)

ROSIE_REMOTE_BANNER = r"""
 ___  ___  ___ ___ ___   ___ ___ __  __  ___ _____ ___
| _ \/ _ \/ __|_ _| __| | _ \ __|  \/  |/ _ \_   _| __|
|   / (_) \__ \| || _|  |   / _|| |\/| | (_) || | | _|
|_|_\\___/|___/___|___| |_|_\___|_|  |_|\___/ |_| |___|
"""

print(ROSIE_REMOTE_BANNER)

# Held flat, buttons up, CENTER at the right thumb (confirmed on hardware).
hub = PrimeHub(top_side=Axis.Z, front_side=-Axis.Y)
radio = BLERadio(REMOTE_BROADCAST_CHANNEL, [])

# Same stop combo as the robot (CENTER is saved for a future feature).
hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

USE_LOW_VOLUME_BEEP = True
hub.speaker.volume(10 if USE_LOW_VOLUME_BEEP else 100)

# Lock = low beep, unlock = high beep, so the driver can tell by ear.
LOCK_BEEP_HZ = 400
UNLOCK_BEEP_HZ = 800
BEEP_MS = 100

# Speed knob: a large motor turned by hand. Its dot is 50%, +/-90 degrees is 100%/0%.
# No reset_angle(0): the motor's absolute zero (the dot) survives power cycles.
SPEED_KNOB_PORT = Port.B
KNOB_MAX_ANGLE = 90

speed_knob = Motor(SPEED_KNOB_PORT)

# Print what we're sending once a second.
PRINT_INTERVAL_MS = 1000
print_timer = StopWatch()

# When the knob moves, show the new speed as a number for a moment.
SPEED_CHANGE_THRESHOLD = 2
SPEED_DISPLAY_MS = 1500
speed_display_timer = StopWatch()
showing_speed = True  # show the speed once at startup

# LEFT toggles wheel lock. Holding RIGHT still runs the arm while locked.
wheels_locked = False
left_was_pressed = False

LOCK_MATRIX = Matrix([
    [0, 100, 100, 100, 0],
    [0, 100, 0, 100, 0],
    [100, 100, 100, 100, 100],
    [100, 100, 0, 100, 100],
    [100, 100, 100, 100, 100],
])


def clamp(value, low, high):
    return max(low, min(high, value))


def ball_matrix(pitch, roll):
    # "Ball on a plane": one lit pixel shows the tilt. Same signs as the robot.
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    tilt_side = clamp(-roll / MAX_TILT_DEG, -1, 1)
    col = int(round(2 + tilt_forward * 2))
    row = int(round(2 + tilt_side * 2))
    grid = [[0] * 5 for _ in range(5)]
    grid[row][col] = 100
    return Matrix(grid)


def bar_matrix(pitch):
    # Attachment mode only uses pitch, so show a full bar instead of a dot.
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    col = int(round(2 + tilt_forward * 2))
    grid = [[0] * 5 for _ in range(5)]
    for row in range(5):
        grid[row][col] = 100
    return Matrix(grid)


def knob_speed_pct():
    knob_angle = clamp(speed_knob.angle(), -KNOB_MAX_ANGLE, KNOB_MAX_ANGLE)
    return int(50 + knob_angle / KNOB_MAX_ANGLE * 50)


prior_speed_pct = knob_speed_pct()
speed_display_timer.reset()

# Only broadcast when the message changes (the radio repeats the last one).
last_message = None

while True:
    speed_pct = knob_speed_pct()

    pitch, roll = hub.imu.tilt()
    pressed = hub.buttons.pressed()

    # LEFT toggles wheel lock -- only on the press itself, not while held.
    left_pressed = Button.LEFT in pressed
    if left_pressed and not left_was_pressed:
        wheels_locked = not wheels_locked
        if wheels_locked:
            hub.speaker.beep(LOCK_BEEP_HZ, BEEP_MS)
            showing_speed = False  # show the lock icon right away
        else:
            hub.speaker.beep(UNLOCK_BEEP_HZ, BEEP_MS)
            # Coming out of lock: remind the driver what speed they're at.
            prior_speed_pct = speed_pct
            showing_speed = True
            speed_display_timer.reset()
        print("Wheels LOCKED" if wheels_locked else "Wheels unlocked")
    left_was_pressed = left_pressed

    if abs(speed_pct - prior_speed_pct) > SPEED_CHANGE_THRESHOLD:
        prior_speed_pct = speed_pct
        showing_speed = True
        speed_display_timer.reset()
    if showing_speed and speed_display_timer.time() >= SPEED_DISPLAY_MS:
        showing_speed = False

    # Hold RIGHT for arm control (works even when wheels are locked).
    if Button.RIGHT in pressed:
        mode = MODE_ATTACHMENT
        normal_icon = bar_matrix(pitch)
    elif wheels_locked:
        mode = MODE_LOCKED
        normal_icon = LOCK_MATRIX
    else:
        mode = MODE_DRIVE
        normal_icon = ball_matrix(pitch, roll)

    if showing_speed:
        # display.number() only goes up to 99, so 100% just shows 99.
        hub.display.number(min(speed_pct, 99))
    else:
        hub.display.icon(normal_icon)

    if print_timer.time() >= PRINT_INTERVAL_MS:
        power_limit = speed_pct / 100
        if mode == MODE_ATTACHMENT:
            arm_pct = MAX_ARM_DUTY_PCT * power_limit
            print(f"Speed percentage: {speed_pct}%  Attachment motor speed: {arm_pct:.0f}% duty cycle")
        elif mode == MODE_LOCKED:
            print(f"Speed percentage: {speed_pct}%  Wheels locked")
        else:
            wheel_speed = MAX_DRIVE_SPEED_MMSEC * power_limit
            print(f"Speed percentage: {speed_pct}%  Wheel motor speed: {wheel_speed:.0f} mm/s")
        print_timer.reset()

    # Zero out values the robot ignores in each mode, so they don't count as a change.
    if mode == MODE_LOCKED:
        message = (MODE_LOCKED, 0, 0, 0)
    elif mode == MODE_ATTACHMENT:
        message = (MODE_ATTACHMENT, speed_pct, pitch, 0)
    else:
        message = (MODE_DRIVE, speed_pct, pitch, roll)

    if message != last_message:
        radio.broadcast(message)
        last_message = message
    wait(100)
