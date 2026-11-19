# m5: drive out, scoop 1, back up, backward S move to the right, straight back in,
# 90 degree launch (two tries, the second a little closer), drive home.
# Start in base, arm on the ground.
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

# Drive from base to the root spot (arm tip just past the red handle).
M5_APPROACH_MM = 780

# Scoop 1: lift the upper root arm.
M5_LIFT_BACK_UP_MM = 30
M5_SCOOP_1_ARM_HEAD_START_MS = 100
M5_ARM_LOWEST_DEGREES = 2  # never lower than this above the start, or the arm falls off
M5_ARM_LIFT_DEGREES = 58
M5_BACK_UP_MM = 80

# Backward S move after scoop 1. Two arcs in reverse that shift the robot right
# without changing its heading. Bigger angle = sharper S (backs up less).
M5_S_RIGHT_MM = 45  # 30 missed left, 60 missed right
M5_S_ARC_DEGREES = 30
# Drive the S slowly (mm/s) so it actually ends where the math says.
M5_S_SPEED_MM_PER_S = 150
# Come back in this much short of where scoop 1 ended (closer was too close).
M5_COME_BACK_SHORT_MM = 50

# Launch.
M5_ARM_LAUNCH_DEGREES = 90
M5_LAUNCH_TIMEOUT_MS = 500
M5_LAUNCH_BACK_UP_MM = 30
M5_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2 = 10000
M5_AFTER_LAUNCH_BACK_UP_MM = 150
# Two tries. Between them: back up, lower the arm, then come back in a little closer
# than the first try (just in case it was too far).
M5_LAUNCH_ATTEMPTS = 2
M5_RETRY_BACK_UP_MM = 50
M5_RETRY_CLOSER_MM = 10


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    # Arm heights are measured from here (arm on the ground).
    start_angle = left_top_motor.angle()
    # Drive to the spot.
    drive_base.straight(M5_APPROACH_MM)

    # Scoop 1: lift the upper root arm while backing up a little.
    move_arm_degrees(left_top_motor, right_top_motor, M5_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, False)
    wait(M5_SCOOP_1_ARM_HEAD_START_MS)
    drive_base.straight(-M5_LIFT_BACK_UP_MM)
    left_top_motor.brake()
    right_top_motor.brake()
    wait(50)
    # Back up with the arm still up (pulls the root out more), then arm almost to the bottom.
    drive_base.straight(-M5_BACK_UP_MM)
    height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
    move_arm_degrees(left_top_motor, right_top_motor, M5_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)

    # S move backward and to the right, then one straight drive back in, ending
    # M5_S_RIGHT_MM to the right (and M5_COME_BACK_SHORT_MM farther back).
    # Each arc: sideways = radius * (1 - cos), backward = radius * sin. Two arcs make the S.
    arc_radians = M5_S_ARC_DEGREES * pi / 180
    s_radius = M5_S_RIGHT_MM / (2 * (1 - cos(arc_radians)))
    s_back_mm = 2 * s_radius * sin(arc_radians)
    drive_base.settings(straight_speed=M5_S_SPEED_MM_PER_S)
    drive_base.arc(s_radius, angle=-M5_S_ARC_DEGREES)  # reverse, curving right
    drive_base.arc(-s_radius, angle=-M5_S_ARC_DEGREES)  # reverse, curving back to straight
    drive_base.settings(straight_speed=DRIVE_SPEED_DEFAULT_MM_PER_S)
    drive_base.straight(M5_BACK_UP_MM + 12 + s_back_mm - M5_COME_BACK_SHORT_MM)

    for attempt in range(M5_LAUNCH_ATTEMPTS):
        # Launch! Full power, then slam to a stop at a fixed height (like a mechanical stop).
        # At the same time, drive backward with a very fast start.
        drive_base.settings(
            straight_acceleration=(M5_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2, DRIVE_SPEED_DECELERATION_MM_PER_S2)
        )
        stop_at = left_top_motor.angle() + M5_ARM_LAUNCH_DEGREES * ARM_GEAR_RATIO
        timer = StopWatch()
        left_top_motor.dc(100)
        right_top_motor.dc(100)
        drive_base.straight(-M5_LAUNCH_BACK_UP_MM, wait=False)
        while left_top_motor.angle() < stop_at and timer.time() < M5_LAUNCH_TIMEOUT_MS:
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

        if attempt < M5_LAUNCH_ATTEMPTS - 1:
            # Another try: back up, arm almost to the bottom, then come back in to
            # M5_RETRY_CLOSER_MM past where this launch started (undoing the launch back-up too).
            drive_base.straight(-M5_RETRY_BACK_UP_MM)
            height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
            move_arm_degrees(left_top_motor, right_top_motor, M5_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)
            drive_base.straight(M5_RETRY_BACK_UP_MM + M5_LAUNCH_BACK_UP_MM + M5_RETRY_CLOSER_MM)

    # Back away, then arm almost to the bottom.
    drive_base.straight(-M5_AFTER_LAUNCH_BACK_UP_MM)
    height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
    move_arm_degrees(left_top_motor, right_top_motor, M5_ARM_LOWEST_DEGREES - height, ARM_SPEED_MEDIUM)

    # Drive home: back to 405 mm from base.
    # Every drive above, added up (the S's backward part cancels out on the way back in).
    distance_from_base = (
        M5_APPROACH_MM
        - M5_LIFT_BACK_UP_MM
        - M5_BACK_UP_MM
        + (M5_BACK_UP_MM + 12 - M5_COME_BACK_SHORT_MM)
        + M5_RETRY_CLOSER_MM * (M5_LAUNCH_ATTEMPTS - 1)
        - M5_LAUNCH_BACK_UP_MM
        - M5_AFTER_LAUNCH_BACK_UP_MM
    )
    drive_base.straight(-(distance_from_base - 405))
    drive_base.turn(25)
    drive_base.straight(-500)
