from rosie_rover import straight_until_done_or_stalled
from pybricks.tools import wait

# Pause between moves while testing. Set to 0 to turn the pauses off.
TEST_DELAY = 3000


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=200)
    # Sets the rover speed to normal
    drive_base.straight(550)
    drive_base.arc(23, angle=65)
    drive_base.straight(280)
    drive_base.turn(23)
    drive_base.settings(straight_speed=85)
    # Sets the rover speed to slow
    straight_until_done_or_stalled(drive_base, 292)
    #Makes the program not die trying
    drive_base.straight(-127)
    # Backs up
    drive_base.settings(straight_speed=250)
    # Sets the rover speed to normal
    drive_base.turn(90)
    straight_until_done_or_stalled(drive_base, 250)
    drive_base.settings(straight_speed=400)
    drive_base.straight(-100)
    drive_base.turn(-65)
    drive_base.arc(230, angle=65)
    drive_base.straight(420)
