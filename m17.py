def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    # Right launch area -> left launch area in one big arc (mirror of m16).
    # Aim just above the Seed pods (about 18 degrees toward the far wall).
    # Negative radius = curve to the left.
    drive_base.arc(-3000, 36)
