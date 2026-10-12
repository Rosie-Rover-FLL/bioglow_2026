from pybricks.tools import wait
from rosie_rover import straight_until_done_or_stalled


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    drive_base.settings(straight_speed=800)
    straight_until_done_or_stalled(drive_base, -400)
    drive_base.straight(345)
    