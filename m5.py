from rosie_rover import (
    ARM_GEAR_RATIO,
    ARM_SLOP_DEGREES,
    ARM_SPEED_MEDIUM,
    ARM_SPEED_SLOW,
    DRIVE_SPEED_ACCELERATION_MM_PER_S2,
    DRIVE_SPEED_DECELERATION_MM_PER_S2,
    move_arm_degrees,
)
from pybricks.tools import StopWatch, wait

# Drive from base to the root spot (arm tip just past the red handle).
M5_APPROACH_MM = 780
# Back up this much WHILE lifting, or the arm jams.
M5_LIFT_BACK_UP_MM = 30
# Head start (ms) for the arm before the back-up begins, so the arm is really moving first.
M5_SCOOP_1_ARM_HEAD_START_MS = 100
M5_SCOOP_2_ARM_HEAD_START_MS = 250

# All arm heights are arm degrees above where the arm started the mission.
# No bottom stop anymore (removed 2026-11-18): the arm rests on the ground, and going
# even 1 degree below the start knocks it off. So "down" never goes lower than this.
M5_ARM_LOWEST_DEGREES = 2

# Stage 1 (once): lift the upper root arm.
M5_ARM_LIFT_DEGREES = 48  # was 38 with the bottom stop
# Then lower the arm this much before backing away.
M5_ARM_LOWER_DEGREES = 20
# Back up this much, lower the arm, come forward the same amount.
M5_BACK_UP_MM = 80

# Stage 2: lift the lower root arm to get ready, then launch.
M5_ARM_PREP_DEGREES = 30  # was 25 with the bottom stop
# Full-power throw, on top of the prep height. The arm is slammed to a stop here
# (it coasts a little past; see the printed overshoot) so it doesn't block the ball.
M5_ARM_LAUNCH_DEGREES = 45
# Safety cap so the throw can never hang if the arm gets stuck.
M5_LAUNCH_TIMEOUT_MS = 500
# Drive backward this much DURING the throw, with a very fast start, to help the
# arm clear the ball at the top. Speed doesn't matter here, only the quick start.
M5_LAUNCH_BACK_UP_MM = 30
M5_LAUNCH_BACK_UP_ACCELERATION_MM_PER_S2 = 10000
# After the last launch, back up this much before lowering the arm.
M5_AFTER_LAUNCH_BACK_UP_MM = 150
# How many times to try the lift + launch. Each retry comes back to the same spot first.
M5_LAUNCH_ATTEMPTS = 2

# Slow-mo video pauses (ms). Set both to 0 when done filming.
M5_VIDEO_START_DELAY = 3000
M5_VIDEO_LIFT_DELAY = 1500


def move_arm_to_height(left_top_motor, right_top_motor, start_angle, height, arm_speed, blocking=True):
    # Moves the arm to `height` arm degrees above the mission's starting position, from
    # wherever it is now. Never goes below M5_ARM_LOWEST_DEGREES, even if an earlier move
    # came up short (e.g. a lift cut off by brake()).
    height = max(height, M5_ARM_LOWEST_DEGREES)
    current_height = (left_top_motor.angle() - start_angle) / ARM_GEAR_RATIO
    move_arm_degrees(left_top_motor, right_top_motor, height - current_height, arm_speed, blocking)


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.use_gyro(True)
    wait(M5_VIDEO_START_DELAY)  # Time to start the camera.
    # Every arm height below is measured from here.
    start_angle = left_top_motor.angle()
    # Drive to the spot (arm starts on the ground).
    drive_base.straight(M5_APPROACH_MM)

    # Stage 1, once: lift the upper root arm while backing up a little (lifting in place jams).
    # Lifts add the slop (gear backlash) on top; lowering takes it back out.
    move_arm_to_height(
        left_top_motor, right_top_motor, start_angle, M5_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, False
    )
    wait(M5_SCOOP_1_ARM_HEAD_START_MS)
    drive_base.straight(-M5_LIFT_BACK_UP_MM)
    left_top_motor.brake()
    right_top_motor.brake()
    wait(50)
    wait(M5_VIDEO_LIFT_DELAY)  # Video pause after the lift.
    # Lower part way, back up, arm (almost) to the bottom, come forward again.
    move_arm_to_height(
        left_top_motor,
        right_top_motor,
        start_angle,
        M5_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES - M5_ARM_LOWER_DEGREES,
        ARM_SPEED_SLOW,
    )
    drive_base.straight(-M5_BACK_UP_MM)
    move_arm_to_height(left_top_motor, right_top_motor, start_angle, M5_ARM_LOWEST_DEGREES, ARM_SPEED_MEDIUM)
    drive_base.straight(M5_BACK_UP_MM + 12)

    for attempt in range(M5_LAUNCH_ATTEMPTS):
        # Stage 2: lift the lower root arm while backing up a little.
        move_arm_to_height(
            left_top_motor, right_top_motor, start_angle, M5_ARM_PREP_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, False
        )
        wait(M5_SCOOP_2_ARM_HEAD_START_MS)
        drive_base.straight(-M5_LIFT_BACK_UP_MM)
        left_top_motor.brake()
        right_top_motor.brake()
        wait(50)
        wait(M5_VIDEO_LIFT_DELAY)  # Video pause after the lift.

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

        # Back down to the prep height.
        move_arm_to_height(
            left_top_motor, right_top_motor, start_angle, M5_ARM_PREP_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_MEDIUM
        )
        if attempt < M5_LAUNCH_ATTEMPTS - 1:
            # Another try coming: back up, arm (almost) to the bottom, come forward to where this attempt started.
            drive_base.straight(-M5_BACK_UP_MM)
            move_arm_to_height(left_top_motor, right_top_motor, start_angle, M5_ARM_LOWEST_DEGREES, ARM_SPEED_MEDIUM)
            drive_base.straight(M5_BACK_UP_MM + M5_LIFT_BACK_UP_MM + M5_LAUNCH_BACK_UP_MM)

    # Last attempt done: back up, arm (almost) to the bottom.
    drive_base.straight(-M5_AFTER_LAUNCH_BACK_UP_MM)
    move_arm_to_height(left_top_motor, right_top_motor, start_angle, M5_ARM_LOWEST_DEGREES, ARM_SPEED_MEDIUM)

    # Drive home: back to 405 mm from base (same end spot as the old version).
    # Every drive above, added up, so changing a distance doesn't move where we end up.
    distance_from_base = (
        M5_APPROACH_MM
        - M5_LIFT_BACK_UP_MM
        - M5_BACK_UP_MM
        + (M5_BACK_UP_MM + 12)
        - M5_LIFT_BACK_UP_MM
        - M5_LAUNCH_BACK_UP_MM
        - M5_AFTER_LAUNCH_BACK_UP_MM
    )
    drive_base.straight(-(distance_from_base - 405))
    drive_base.turn(25)
    drive_base.straight(-500)
