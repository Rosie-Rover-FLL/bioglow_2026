REMOTE_BROADCAST_CHANNEL = 1  # remote broadcasts here, robot observes it
ROBOT_BROADCAST_CHANNEL = 2  # robot's own channel, unused for now

# Tilt angle (either axis) that counts as "full power". Shared so the
# remote's ball-position display and the robot's power scaling agree on
# what "full tilt" means. Confirmed against real hardware -- see
# REMOTE_PLAN.md's "Tilt calibration" section.
MAX_TILT_DEG = 45

MODE_DRIVE = 0
MODE_ATTACHMENT = 1
