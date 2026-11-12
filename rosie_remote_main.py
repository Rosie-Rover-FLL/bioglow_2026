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

# Held flat, buttons facing up, CENTER button toward the driver's right
# thumb, BLUETOOTH button toward the front-left corner. Confirmed correct
# on real hardware (2026-08-31): tilting forward/backward barely moves
# roll, and tilting left/right barely moves pitch.
hub = PrimeHub(top_side=Axis.Z, front_side=-Axis.Y)
radio = BLERadio(REMOTE_BROADCAST_CHANNEL, [])

# Same stop combo as the robot -- CENTER is reserved for something else
# (coming soon), so it can't be the lone stop button here either.
hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

# Same quiet/full volume switch as the robot.
USE_LOW_VOLUME_BEEP = True
hub.speaker.volume(10 if USE_LOW_VOLUME_BEEP else 100)

# Lock = low beep, unlock = high beep, so the driver can tell by ear.
LOCK_BEEP_HZ = 400
UNLOCK_BEEP_HZ = 800
BEEP_MS = 100

# Speed knob: a large motor turned by hand, never driven. Large motors have
# a physical dot marking their true absolute zero, which persists across
# power cycles -- so we deliberately do NOT call reset_angle(0) here. The
# dot position (angle 0) is 50% speed; confirmed on real hardware
# (2026-08-31) that +/-90 degrees from the dot reaches 100%/0%.
SPEED_KNOB_PORT = Port.B
KNOB_MAX_ANGLE = 90

speed_knob = Motor(SPEED_KNOB_PORT)

# Non-blocking "print what we're sending" -- checked every loop but only
# actually prints once the timer clears 1 second, so it doesn't slow down
# the ~100ms broadcast/display cadence.
PRINT_INTERVAL_MS = 1000
print_timer = StopWatch()

# Speed knob readout: when the knob moves more than SPEED_CHANGE_THRESHOLD
# away from the last value we showed, show the new value as a number for
# SPEED_DISPLAY_MS, then go back to the normal dot/bar/lock display.
SPEED_CHANGE_THRESHOLD = 2
SPEED_DISPLAY_MS = 1500
speed_display_timer = StopWatch()
showing_speed = True  # show the speed once at startup

# Wheel lock: LEFT toggles it. While locked the wheels never get a drive
# command (we send MODE_LOCKED, which stops everything), but holding RIGHT
# still runs the arm like normal. Starts unlocked.
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
    # "Ball on a plane": pitch moves the lit pixel along columns (forward
    # = col 4, backward = col 0), roll moves it along rows (left = row 0,
    # right = row 4), center = (2, 2). Same sign convention as the robot's
    # tilt_forward/tilt_side, confirmed on real hardware 2026-08-31.
    tilt_forward = clamp(-pitch / MAX_TILT_DEG, -1, 1)
    tilt_side = clamp(-roll / MAX_TILT_DEG, -1, 1)
    col = int(round(2 + tilt_forward * 2))
    row = int(round(2 + tilt_side * 2))
    grid = [[0] * 5 for _ in range(5)]
    grid[row][col] = 100
    return Matrix(grid)


def bar_matrix(pitch):
    # Attachment mode only cares about pitch (both arm motors always move
    # together), so the display is a full vertical bar instead of a single
    # dot -- same column math as ball_matrix, every row lit.
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

# Last message handed to the radio. We only call broadcast() when the
# message actually changes -- the radio keeps advertising the last message
# on its own, so re-sending the same thing is pointless.
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

    # Hold RIGHT for attachment-control mode (works even when wheels are
    # locked); both arm motors always move together in that mode, so there's
    # no need for a force sensor or any per-motor lock.
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

    # Only send what the robot actually uses in each mode, so values it
    # ignores (e.g. tilt while locked) don't count as a "change". Locked is
    # always the exact same message, so it's sent once and then left alone.
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
