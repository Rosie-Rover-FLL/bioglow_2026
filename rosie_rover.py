from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Drive speed, mm/s (max 742). Times = m16 at this speed.
DRIVE_SPEED_DEFAULT_MM_PER_S = 450  # Medium, m16 ~4.8 s (est.)
# DRIVE_SPEED_DEFAULT_MM_PER_S = 600  # Faster, m16 ~4.0 s (est.)
# DRIVE_SPEED_DEFAULT_MM_PER_S = 700  # Fastest, m16 ~3.7 s (est.)

# Drive start, mm/s² (lower = less wheel slip)
# DRIVE_SPEED_ACCELERATION_MM_PER_S2 = 200  # Very slow start, m16 ~4.8 s (est.)
# DRIVE_SPEED_ACCELERATION_MM_PER_S2 = 350  # Slow start, m16 ~4.0 s (est.)
DRIVE_SPEED_ACCELERATION_MM_PER_S2 = 500  # Could slip a little, m16 ~3.7 s (est.)
# DRIVE_SPEED_ACCELERATION_MM_PER_S2 = 1000  # Near the default which slipped some.
DRIVE_SPEED_DECELERATION_MM_PER_S2 = 1113  # Pybricks default

# Turn speed, deg/s (max 773)
# TURN_RATE_DEFAULT_DEG_PER_S = 200  # Slower
TURN_RATE_DEFAULT_DEG_PER_S = 260  # Medium (Pybricks default)
# TURN_RATE_DEFAULT_DEG_PER_S = 400  # Faster, only helps big turns

# Turn start, deg/s² (lower = less wheel slip)
TURN_RATE_ACCELERATION_DEG_PER_S2 = 580 # Lower than the default 1159 to reduce slip
TURN_RATE_DECELERATION_DEG_PER_S2 = 1159  # Pybricks default

# True = steer with the gyro. Re-test turns if you change this!
USE_GYRO = False

# Pause between moves while testing, ms. Set to 0 to turn the pauses off.
# Shared by every mission that uses wait(TEST_DELAY).
# TEST_DELAY = 3000
TEST_DELAY = 0


def setup():
    left_wheel = Motor(Port.D, Direction.COUNTERCLOCKWISE)
    right_wheel = Motor(Port.B, Direction.CLOCKWISE)
    left_top_motor = Motor(Port.C, Direction.CLOCKWISE)
    right_top_motor = Motor(Port.E, Direction.COUNTERCLOCKWISE)
    left_color_sensor = ColorSensor(Port.F)
    right_color_sensor = ColorSensor(Port.A)
    prime_hub = PrimeHub(top_side=Axis.Z, front_side=-Axis.Y)
    drive_base = DriveBase(left_wheel, right_wheel, 85, 110)
    reset_drive_settings(drive_base)
    return (
        left_top_motor,
        right_top_motor,
        left_color_sensor,
        right_color_sensor,
        prime_hub,
        drive_base,
    )


def reset_drive_settings(drive_base):
    # Runs before every mission, so the last mission's settings don't carry over.
    drive_base.settings(
        straight_speed=DRIVE_SPEED_DEFAULT_MM_PER_S,
        straight_acceleration=(DRIVE_SPEED_ACCELERATION_MM_PER_S2, DRIVE_SPEED_DECELERATION_MM_PER_S2),
        turn_rate=TURN_RATE_DEFAULT_DEG_PER_S,
        turn_acceleration=(TURN_RATE_ACCELERATION_DEG_PER_S2, TURN_RATE_DECELERATION_DEG_PER_S2),
    )
    drive_base.use_gyro(USE_GYRO)


def print_battery(prime_hub):
    print(f"Battery voltage: {prime_hub.battery.voltage()} mV")


def straight_until_done_or_stalled(drive_base, distance):
    # Stops early if stuck.
    drive_base.straight(distance, wait=False)
    while not drive_base.done():
        if drive_base.stalled():
            drive_base.stop()
            break
        wait(10)


def arm_until_done_or_stalled(left_top_motor, right_top_motor, speed, angle):
    # Moves both arm motors. If either gets stuck, both stop.
    left_top_motor.run_angle(speed, angle, wait=False)
    right_top_motor.run_angle(speed, angle, wait=False)
    while not (left_top_motor.done() and right_top_motor.done()):
        if left_top_motor.stalled() or right_top_motor.stalled():
            left_top_motor.stop()
            right_top_motor.stop()
            break
        wait(10)

