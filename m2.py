from pybricks.tools import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=450)
    drive_base.straight(350)

    # Start both arm motors, then wait until each one is done OR stalled.
    left_top_motor.run_angle(200, 180, wait=False)
    right_top_motor.run_angle(200, 180, wait=False)
    while not (
        (left_top_motor.done() or left_top_motor.stalled())
        and (right_top_motor.done() or right_top_motor.stalled())
    ):
        wait(10)
    # Lock both arms where they are, so a stalled motor stops pushing.
    left_top_motor.hold()
    right_top_motor.hold()

    drive_base.straight(-350)
    left_top_motor.run_angle(200, -180, wait=False)
    right_top_motor.run_angle(200, -180, wait=False)
    while not (left_top_motor.done() and right_top_motor.done()):
        wait(10)
    
