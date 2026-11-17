from rosie_rover import (
    ARM_ACCELERATION_DEFAULT,
    ARM_ACCELERATION_MAX,
    ARM_SLOP_DEGREES,
    ARM_SPEED_FAST,
    ARM_SPEED_MEDIUM,
    ARM_SPEED_SLOW,
    move_arm_degrees,
)
from pybricks.tools import wait

# Drive from base to the root spot (arm tip just past the red handle).
M5_APPROACH_MM = 790
# Back up this much WHILE lifting, or the arm jams.
M5_LIFT_BACK_UP_MM = 30

# Stage 1 (once): lift the upper root arm.
M5_ARM_LIFT_DEGREES = 38
# Then lower the arm this much before backing away.
M5_ARM_LOWER_DEGREES = 20
# Back up this much, lower the arm to the bottom, come forward the same amount.
M5_BACK_UP_MM = 80

# Stage 2: lift the lower root arm to get ready, then launch.
M5_ARM_PREP_DEGREES = 25
# Fast throw, on top of the prep height.
M5_ARM_LAUNCH_DEGREES = 60
# After the launch, back up this much before lowering the arm.
M5_AFTER_LAUNCH_BACK_UP_MM = 150


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Gyro on for this mission (reset to off before every mission).
    drive_base.use_gyro(True)
    # Drive to the spot (arm starts at the bottom).
    drive_base.straight(M5_APPROACH_MM)

    # Stage 1, once: lift the upper root arm while backing up a little (lifting in place jams).
    move_arm_degrees(
        left_top_motor, right_top_motor, M5_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, blocking=False
    )
    drive_base.straight(-M5_LIFT_BACK_UP_MM)
    left_top_motor.brake()
    right_top_motor.brake()
    wait(50)
    # Lower part way, back up, arm to the bottom, come forward again.
    move_arm_degrees(left_top_motor, right_top_motor, -M5_ARM_LOWER_DEGREES, ARM_SPEED_SLOW)
    drive_base.straight(-M5_BACK_UP_MM)
    # The rest of the way down. Includes the slop, so the motor ends where it started.
    move_arm_degrees(
        left_top_motor,
        right_top_motor,
        -(M5_ARM_LIFT_DEGREES + ARM_SLOP_DEGREES - M5_ARM_LOWER_DEGREES),
        ARM_SPEED_MEDIUM,
    )
    drive_base.straight(M5_BACK_UP_MM + 12)

    # Stage 2: lift the lower root arm while backing up a little.
    move_arm_degrees(
        left_top_motor, right_top_motor, M5_ARM_PREP_DEGREES + ARM_SLOP_DEGREES, ARM_SPEED_SLOW, blocking=False
    )
    drive_base.straight(-M5_LIFT_BACK_UP_MM)
    left_top_motor.brake()
    right_top_motor.brake()
    wait(50)

    # Launch! Max acceleration for the throw only, then back to the default.
    left_top_motor.control.limits(acceleration=ARM_ACCELERATION_MAX)
    right_top_motor.control.limits(acceleration=ARM_ACCELERATION_MAX)
    move_arm_degrees(left_top_motor, right_top_motor, M5_ARM_LAUNCH_DEGREES, ARM_SPEED_FAST)
    left_top_motor.control.limits(acceleration=ARM_ACCELERATION_DEFAULT)
    right_top_motor.control.limits(acceleration=ARM_ACCELERATION_DEFAULT)

    # Back down to the prep height, back up, arm to the bottom.
    move_arm_degrees(left_top_motor, right_top_motor, -M5_ARM_LAUNCH_DEGREES, ARM_SPEED_MEDIUM)
    drive_base.straight(-M5_AFTER_LAUNCH_BACK_UP_MM)
    move_arm_degrees(left_top_motor, right_top_motor, -(M5_ARM_PREP_DEGREES + ARM_SLOP_DEGREES), ARM_SPEED_MEDIUM)

    # Drive home: back to 405 mm from base (same end spot as the old version).
    # Every drive above, added up, so changing a distance doesn't move where we end up.
    distance_from_base = (
        M5_APPROACH_MM
        - M5_LIFT_BACK_UP_MM
        - M5_BACK_UP_MM
        + (M5_BACK_UP_MM + 12)
        - M5_LIFT_BACK_UP_MM
        - M5_AFTER_LAUNCH_BACK_UP_MM
    )
    drive_base.straight(-(distance_from_base - 405))
    drive_base.turn(25)
    drive_base.straight(-500)
