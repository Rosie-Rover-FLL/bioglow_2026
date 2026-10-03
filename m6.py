from rosie_rover import straight_until_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=200)
    # Sets the rover speed to normal
    drive_base.straight(550)
    drive_base.arc(23, angle=65)
    drive_base.straight(200)
    drive_base.turn(18)
    drive_base.settings(straight_speed=85)
    # Sets the rover speed to slow
    straight_until_stalled(drive_base, 292)
    #Makes the program not die trying
    drive_base.straight(-127)
    # Backs up
    drive_base.settings(straight_speed=200)
    # Sets the rover speed to normal
    drive_base.turn(95)
    drive_base.straight(830)