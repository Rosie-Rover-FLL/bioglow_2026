from pybricks.parameters import Stop


def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):

    drive_base.settings(straight_speed=700)  # near max (742), leaves the outer wheel room on the arc

    # Old simple arc aim
    # Aim just above the Seed pods (about 18 degrees toward the far wall).
    # drive_base.arc(-3000, 36)

    # Newer start on the wall
    drive_base.arc(-280, 78, then=Stop.NONE)   # tight left turn to get off the wall
    drive_base.arc(-1600, 14, then=Stop.NONE)  # gentle left, up to the top of the hill
    drive_base.arc(-1250, 16, then=Stop.NONE)  # gentle left, heading down toward home
    drive_base.straight(620)                    # straight into the left launch area
