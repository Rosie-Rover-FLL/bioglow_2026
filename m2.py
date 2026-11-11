from pybricks.tools import wait
from rosie_rover import arm_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Slow start (200 mm/s²) to avoid wheel slip, normal stop (800 mm/s²).
    drive_base.settings(straight_speed=450, straight_acceleration=(200, 800))
    drive_base.straight(265)

    # Raise the arm.
    arm_until_done_or_stalled(left_top_motor, right_top_motor, 950, 180)

    # Drive back and lower the arm at the same time, so it's ready for a
    # rerun. wait=False starts the drive without waiting for it to finish.
    drive_base.straight(-350, wait=False)
    arm_until_done_or_stalled(left_top_motor, right_top_motor, -500, 180)
    while not drive_base.done():
        wait(10)
