from pybricks.hubs import PrimeHub
from pybricks.messaging import BLERadio
from pybricks.parameters import Axis, Button, Port
from pybricks.pupdevices import Motor
from pybricks.tools import Matrix, wait

from remote_protocol import (
    MAX_TILT_DEG,
    MODE_ATTACHMENT,
    MODE_DRIVE,
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
# roll, and tilting left/right barely moves pitch -- see REMOTE_PLAN.md.
hub = PrimeHub(top_side=Axis.Z, front_side=-Axis.Y)
radio = BLERadio(REMOTE_BROADCAST_CHANNEL, [])

# Same stop combo as the robot -- CENTER is reserved for something else
# (coming soon), so it can't be the lone stop button here either.
hub.system.set_stop_button((Button.CENTER, Button.BLUETOOTH))

# Speed knob: a large motor turned by hand, never driven. Large motors have
# a physical dot marking their true absolute zero, which persists across
# power cycles -- so we deliberately do NOT call reset_angle(0) here. The
# dot position (angle 0) is 50% speed; confirmed on real hardware
# (2026-08-31) that +/-90 degrees from the dot reaches 100%/0%.
SPEED_KNOB_PORT = Port.A
KNOB_MAX_ANGLE = 90

speed_knob = Motor(SPEED_KNOB_PORT)


def clamp(value, low, high):
    return max(low, min(high, value))


def ball_matrix(pitch, roll):
    # "Ball on a plane": pitch moves the lit pixel along columns (forward
    # = col 4, backward = col 0), roll moves it along rows (left = row 0,
    # right = row 4), center = (2, 2). Same sign convention as the robot's
    # tilt_forward/tilt_side, confirmed on real hardware -- see
    # REMOTE_PLAN.md's "Tilt calibration" section.
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


while True:
    knob_angle = clamp(speed_knob.angle(), -KNOB_MAX_ANGLE, KNOB_MAX_ANGLE)
    speed_pct = int(50 + knob_angle / KNOB_MAX_ANGLE * 50)

    pitch, roll = hub.imu.tilt()

    # Hold LEFT for attachment-control mode; both arm motors always move
    # together in that mode, so there's no need for a force sensor or any
    # per-motor lock.
    if Button.LEFT in hub.buttons.pressed():
        mode = MODE_ATTACHMENT
        hub.display.icon(bar_matrix(pitch))
    else:
        mode = MODE_DRIVE
        hub.display.icon(ball_matrix(pitch, roll))

    radio.broadcast((mode, speed_pct, pitch, roll))
    wait(100)
