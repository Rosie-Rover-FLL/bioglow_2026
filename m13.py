from concurrent.futures import wait


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    
    # creature in box 1/2 from
    drive_base.straight(203)
    left_top_motor.dc(-70)
    right_top_motor.dc(-70)
    wait(1000)
    left_top_motor.stop()
    right_top_motor.stop()
    drive_base.straight(-203)