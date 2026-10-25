def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Left launch area -> right launch area in one big arc.
    # Aim at the Forest Elder (about 18 degrees toward the far wall).
    # Positive radius = curve to the right.
    drive_base.arc(3000, 36)
