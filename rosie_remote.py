from pybricks.hubs import PrimeHub
from pybricks.messaging import BLERadio
from pybricks.parameters import Axis, Button, Port
from pybricks.pupdevices import Motor  # ForceSensor unused, no sensor yet
from pybricks.tools import Matrix, wait

from remote_protocol import (
    LOCK_LEFT,
    LOCK_NONE,
    LOCK_RIGHT,
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

# Speed knob: a large motor turned by hand, never driven. Large motors have
# a physical dot marking their true absolute zero, which persists across
# power cycles -- so we deliberately do NOT call reset_angle(0) here. The
# dot position (angle 0) is 50% speed; confirmed on real hardware
# (2026-08-31) that +/-90 degrees from the dot reaches 100%/0%.
SPEED_KNOB_PORT = Port.A
KNOB_MAX_ANGLE = 90

speed_knob = Motor(SPEED_KNOB_PORT)

# Force sensor doubles as a pushbutton: held down = attachment-control mode.
# Commented out -- no force sensor on hand yet. Restore once one is
# available (see the `mode_button.pressed()` branch below, also disabled).
# FORCE_SENSOR_PORT = Port.B
# mode_button = ForceSensor(FORCE_SENSOR_PORT)


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


while True:
    knob_angle = clamp(speed_knob.angle(), -KNOB_MAX_ANGLE, KNOB_MAX_ANGLE)
    speed_pct = int(50 + knob_angle / KNOB_MAX_ANGLE * 50)

    pitch, roll = hub.imu.tilt()
    hub.display.icon(ball_matrix(pitch, roll))

    # No force sensor on hand yet, so attachment mode is unreachable for
    # now -- always broadcasting drive mode. Restore this branch once a
    # force sensor is available:
    # if mode_button.pressed():
    #     mode = MODE_ATTACHMENT
    #     pressed = hub.buttons.pressed()
    #     if Button.LEFT in pressed:
    #         lock = LOCK_LEFT
    #     elif Button.RIGHT in pressed:
    #         lock = LOCK_RIGHT
    #     else:
    #         lock = LOCK_NONE
    # else:
    #     mode = MODE_DRIVE
    #     lock = LOCK_NONE
    mode = MODE_DRIVE
    lock = LOCK_NONE

    radio.broadcast((mode, speed_pct, pitch, roll, lock))
    wait(100)
