# TEMPORARY full test version of m5: drive out, scoop 1, back up, backward S move 30 mm
# to the right, straight back in, 90 degree launch (no scoop 2), drive home.
# If it works better than m5, it replaces m5. Start in base like m5, arm on the ground.
from rosie_rover import (
    ARM_GEAR_RATIO,
    ARM_SLOP_DEGREES,
    ARM_SPEED_MEDIUM,
    ARM_SPEED_SLOW,
    DRIVE_SPEED_ACCELERATION_MM_PER_S2,
    DRIVE_SPEED_DECELERATION_MM_PER_S2,
    DRIVE_SPEED_DEFAULT_MM_PER_S,
    move_arm_degrees,
)
from pybricks.tools import StopWatch, wait
from umath import cos, pi, sin

# Drive from base to the root spot (same as m5).
M8_APPROACH_MM = 780

# Scoop 1 (same as m5).
M8_LIFT_BACK_UP_MM = 30
M8_SCOOP_1_ARM_HEAD_START_MS = 100
M8_ARM_LOWEST_DEGREES = 2  # never lower than this above the start, or the arm falls off
M8_ARM_LIFT_DEGREES = 58
M8_BACK_UP_MM = 80

# NEW: backward S move after scoop 1. Two arcs in reverse that shift the robot right
# without changing its heading. Bigger angle = sharper S (backs up less).
M8_S_RIGHT_MM = 45  # 30 missed left, 60 missed right
M8_S_ARC_DEGREES = 30
# Drive the S slowly (mm/s) so it actually ends where the math says.
M8_S_SPEED_MM_PER_S = 150
# Stop this much short of m5's spot when coming back in after the S (was too close).
M8_COME_BACK_SHORT_MM = 50

# Launch.
M8_ARM_LAUNCH_DEGREES = 90
M8_LAUNCH_TIMEOUT_MS = 500
M8_LAUNCH_BACK_UP_MM = 30
M8_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2 = 10000
M8_AFTER_LAUNCH_BACK_UP_MM = 150
# Two tries. Between them: back up, lower the arm, then come back in a little closer
# than the first try (just in case it was too far).
M8_LAUNCH_ATTEMPTS = 2
M8_RETRY_BACK_UP_MM = 50
M8_RETRY_CLOSER_MM = 10

# Slow-mo video pauses (ms).
M8_VIDEO_START_DELAY = 3000
M8_VIDEO_LIFT_DELAY = 1500


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    wait(M8_VIDEO_START_DELAY)  # Time to start the camera.
    # Arm heights are measured from here (arm on the ground).
    start_angle = left_top_motor.angle()
    # Drive to the spot.
    drive_base.straight(M8_APPROACH_MM)

    # Scoop 1: lift the upper root arm while backing up a little.
    move_arm_degrees(left_top_motor, right_top_motor, M8_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, False)
    wait(M8_SCOOP_1_ARM_HEAD_START_MS)
    drive_base.straight(-M8_LIFT_BACK_UP_MM)
    left_top_motor.brake()
    right_top_motor.brake()
    wait(50)
    wait(M8_VIDEO_LIFT_DELAY)
    # Back up with the arm still up (pulls the root out more), then arm almost to the bottom.
    drive_base.straight(-M8_BACK_UP_MM)
    height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
    move_arm_degrees(left_top_motor, right_top_motor, M8_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)

    # NEW: S move backward and to the right, then one straight drive back in, ending
    # M8_S_RIGHT_MM right of where scoop 1 started its lift and 18 mm behind it (same spot
    # m5 comes back to: -30 - 80 + 92).
    # Each arc: sideways = radius * (1 - cos), backward = radius * sin. Two arcs make the S.
    arc_radians = M8_S_ARC_DEGREES * pi / 180
    s_radius = M8_S_RIGHT_MM / (2 * (1 - cos(arc_radians)))
    s_back_mm = 2 * s_radius * sin(arc_radians)
    drive_base.settings(straight_speed=M8_S_SPEED_MM_PER_S)
    drive_base.arc(s_radius, angle=-M8_S_ARC_DEGREES)  # reverse, curving right
    drive_base.arc(-s_radius, angle=-M8_S_ARC_DEGREES)  # reverse, curving back to straight
    drive_base.settings(straight_speed=DRIVE_SPEED_DEFAULT_MM_PER_S)
    drive_base.straight(M8_BACK_UP_MM + 12 + s_back_mm - M8_COME_BACK_SHORT_MM)
    wait(M8_VIDEO_LIFT_DELAY)

    for attempt in range(M8_LAUNCH_ATTEMPTS):
        # Launch! Full power, then slam to a stop at a fixed height (like a mechanical stop).
        # At the same time, drive backward with a very fast start.
        drive_base.settings(
            straight_acceleration=(M8_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2, DRIVE_SPEED_DECELERATION_MM_PER_S2)
        )
        stop_at = left_top_motor.angle() + M8_ARM_LAUNCH_DEGREES * ARM_GEAR_RATIO
        timer = StopWatch()
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

        if attempt < M8_LAUNCH_ATTEMPTS - 1:
            # Another try: back up, arm almost to the bottom, then come back in to
            # M8_RETRY_CLOSER_MM past where this launch started (undoing the launch back-up too).
            drive_base.straight(-M8_RETRY_BACK_UP_MM)
            height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
            move_arm_degrees(left_top_motor, right_top_motor, M8_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)
            drive_base.straight(M8_RETRY_BACK_UP_MM + M8_LAUNCH_BACK_UP_MM + M8_RETRY_CLOSER_MM)
            wait(M8_VIDEO_LIFT_DELAY)

    # Back away, then arm almost to the bottom.
    drive_base.straight(-M8_AFTER_LAUNCH_BACK_UP_MM)
    height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
    move_arm_degrees(left_top_motor, right_top_motor, M8_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)

    # Drive home: back to 405 mm from base (same end spot as m5).
    # Every drive above, added up (the S's backward part cancels out on the way back in).
    distance_from_base = (
        M8_APPROACH_MM
        - M8_LIFT_BACK_UP_MM
        - M8_BACK_UP_MM
        + (M8_BACK_UP_MM + 12 - M8_COME_BACK_SHORT_MM)
        + M8_RETRY_CLOSER_MM * (M8_LAUNCH_ATTEMPTS - 1)
        - M8_LAUNCH_BACK_UP_MM
        - M8_AFTER_LAUNCH_BACK_UP_MM
    )
    drive_base.straight(-(distance_from_base - 405))
    drive_base.turn(25)
    drive_base.straight(-500)
