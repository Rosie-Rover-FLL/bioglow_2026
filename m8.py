# TEMPORARY test mission: m5's launch only. Delete when m5 is tuned.
# Set up by hand: robot and root in the spot m5 reaches after both scoops,
# arm already lifted to the (higher) second-scoop height. m8 drops 20, then launches 40.
# Numbers copied from m5.py; change them here to experiment, then copy the winners back to m5.
from rosie_rover import (
    ARM_GEAR_RATIO,
    ARM_SPEED_MEDIUM,
    DRIVE_SPEED_ACCELERATION_MM_PER_S2,
    DRIVE_SPEED_DECELERATION_MM_PER_S2,
    move_arm_degrees,
)
from pybricks.tools import StopWatch, wait

# Full-power drop right before the launch (start the arm at least ~25 degrees up, or it hits the ground).
M8_ARM_DROP_DEGREES = 20
# Launch is measured from the bottom of the drop.
M8_ARM_LAUNCH_DEGREES = 40  # 45 and 20 both failed 2026-11-19 (20 overshot only ~2 degrees)
M8_LAUNCH_TIMEOUT_MS = 500
M8_LAUNCH_BACK_UP_MM = 30
M8_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2 = 10000
# Time to start the camera.
M8_VIDEO_START_DELAY = 3000


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    wait(M8_VIDEO_START_DELAY)
    start_angle = left_top_motor.angle()

    # Hard drop first: full power down, then straight into the launch with no stop in
    # between, so the arm hits the root on the way down and bounces right back up.
    drop_to = left_top_motor.angle() - M8_ARM_DROP_DEGREES * ARM_GEAR_RATIO
    timer = StopWatch()
    left_top_motor.dc(-100)
    right_top_motor.dc(-100)
    while left_top_motor.angle() > drop_to and timer.time() < M8_LAUNCH_TIMEOUT_MS:
        wait(1)

    # Launch! Full power, then slam to a stop at a fixed height (like a mechanical stop).
    # At the same time, drive backward with a very fast start.
    drive_base.settings(
        straight_acceleration=(M8_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2, DRIVE_SPEED_DECELERATION_MM_PER_S2)
    )
    stop_at = left_top_motor.angle() + M8_ARM_LAUNCH_DEGREES * ARM_GEAR_RATIO
    timer.reset()
    left_top_motor.dc(100)
    right_top_motor.dc(100)
    drive_base.straight(-M8_LAUNCH_BACK_UP_MM, wait=False)
    while left_top_motor.angle() < stop_at and timer.time() < M8_LAUNCH_TIMEOUT_MS:
        wait(1)
    left_top_motor.hold()
    right_top_motor.hold()
    # Let the back-up finish (capped, so it can't hang), then normal acceleration again.
    while not drive_base.done() and timer.time() < 2000:
        wait(10)
    drive_base.settings(
        straight_acceleration=(DRIVE_SPEED_ACCELERATION_MM_PER_S2, DRIVE_SPEED_DECELERATION_MM_PER_S2)
    )
    wait(100)  # Let the arm settle before measuring.
    print("Launch overshoot (arm degrees):", (left_top_motor.angle() - stop_at) / ARM_GEAR_RATIO)

    # Back down to where the arm started (the prep height), ready to set up the next try.
    move_arm_degrees(
        left_top_motor, right_top_motor, -(left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO, ARM_SPEED_MEDIUM
    )
