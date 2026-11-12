from rosie_rover import straight_until_done_or_stalled
from pybricks.tools import wait

# Pause between moves while testing. Set to 0 to turn the pauses off.
# TEST_DELAY = 3000
TEST_DELAY = 0


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    wait(TEST_DELAY)
    drive_base.straight(635)
    wait(TEST_DELAY)
    drive_base.turn(-30)
    wait(TEST_DELAY)
    left_top_motor.dc(100)
    right_top_motor.dc(100)
    wait(150)
    right_top_motor.brake()
    left_top_motor.brake()
    wait(TEST_DELAY)
    drive_base.turn(25)
    wait(TEST_DELAY)
    drive_base.straight(-635)
