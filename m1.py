import rosie_rover
from pybricks.tools import wait

def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=800)
    drive_base.straight(-550)
    drive_base.straight(550)


if __name__ == "__main__":
    run(*rosie_rover.setup())
