REMOTE_BROADCAST_CHANNEL = 1  # remote broadcasts here, robot observes it
ROBOT_BROADCAST_CHANNEL = 2  # robot's own channel, unused for now

# Tilt (either axis) that counts as full power. Full tips measured 46-54 degrees.
MAX_TILT_DEG = 45

# Max values at 100% knob power (shared so the remote's printout matches the robot).
MAX_DRIVE_SPEED_MMSEC = 500
MAX_ARM_DUTY_PCT = 70

MODE_DRIVE = 0
MODE_ATTACHMENT = 1
# Wheels locked on the remote: robot stops everything.
MODE_LOCKED = 2
