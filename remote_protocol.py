REMOTE_BROADCAST_CHANNEL = 1  # remote broadcasts here, robot observes it
ROBOT_BROADCAST_CHANNEL = 2  # robot's own channel, unused for now

# Tilt angle (either axis) that counts as "full power". Shared so the
# remote's ball-position display and the robot's power scaling agree on
# what "full tilt" means. Measured on real hardware (2026-08-31): full
# tips reach 46-54 degrees, so 45 gives a little headroom before max power.
MAX_TILT_DEG = 45

# Ceiling values at 100% knob power. Shared so the remote's own status
# print (mm/s and duty cycle it's about to ask for) matches what the robot
# actually does with the same speed_pct.
MAX_DRIVE_SPEED_MMSEC = 500
MAX_ARM_DUTY_PCT = 70

MODE_DRIVE = 0
MODE_ATTACHMENT = 1
