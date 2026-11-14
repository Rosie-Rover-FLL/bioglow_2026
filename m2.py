from pybricks.tools import wait
from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Gyro on for this mission (reset to off before every mission).
    drive_base.use_gyro(True)
    # Slow start (200 mm/s²) to avoid wheel slip, normal stop (800 mm/s²).
    drive_base.settings(straight_speed=450, straight_acceleration=(550, 800))
    drive_base.straight(285)

    # Raise the arm with everything maxed out: full speed (1000 deg/s) and
    # the firmware's highest start/stop acceleration (20000 deg/s², default
    # is 2000). Strength (torque) is already at max by default.
    left_top_motor.control.limits(acceleration=20000)
    right_top_motor.control.limits(acceleration=20000)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, 1000, 210)
    # Back to the default so other missions (and the lowering below) aren't affected.
    left_top_motor.control.limits(acceleration=2000)
    right_top_motor.control.limits(acceleration=2000)

    # Drive back and lower the arm at the same time, so it's ready for a
    # rerun. wait=False starts the drive without waiting for it to finish.
    drive_base.straight(-350, wait=False)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, -500, 180)
    while not drive_base.done():
        wait(10)
