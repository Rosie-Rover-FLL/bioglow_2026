from rosie_rover import straight_until_done_or_stalled
from pybricks.tools import wait

# Pause between moves while testing. Set to 0 to turn the pauses off.
TEST_DELAY = 3000


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    wait(0)
    drive_base.straight(635)
    wait(0)
    right_wheel.run_angle(500, 25)
    wait(0)
    left_top_motor.dc(100)
    right_top_motor.dc(100)
    wait(150)
    right_top_motor.brake()
    left_top_motor.brake()