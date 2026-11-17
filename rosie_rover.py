from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait

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

# Arm gearing: 12-tooth gear on the motor drives a 20-tooth gear on the arm,
# so 1 motor degree = 12/20 arm degree. move_arm_degrees() does this math for you.
ARM_GEAR_RATIO = 20 / 12  # motor degrees per arm degree

# Extra arm degrees for the FIRST lift from the bottom stop. The gears are loose
# at first, so the motor turns a bit before the arm starts to move.
# Measured with m8 (2026-11-17, 1 test): a 10° lift only moved the arm ~4°.
ARM_SLOP_DEGREES = 6

# Arm speed, ARM deg/s (max 600 = motor max 1000 x 12/20)
ARM_SPEED_SLOW = 90
ARM_SPEED_MEDIUM = 240
ARM_SPEED_FAST = 600

# Arm motor start/stop acceleration, MOTOR deg/s² (max 20000).
# reset_arm_settings() sets the default before every mission. To change it, call
# left_top_motor.control.limits(acceleration=...) (same for right) before move_arm_degrees().
ARM_ACCELERATION_DEFAULT = 2000  # Pybricks default
ARM_ACCELERATION_MAX = 20000

# Reflection (0-100%) that counts as white. White ~90+, black ~10. Not measured yet.
WHITE_LINE_MIN_REFLECTION = 80

# True = print color sensor readings every 50 ms while looking for the white line.
PRINT_DEBUG_LINE_SENSOR_READINGS = True

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


def reset_arm_settings(left_top_motor, right_top_motor):
    # Runs before every mission, so one mission's arm acceleration doesn't carry over.
    left_top_motor.control.limits(acceleration=ARM_ACCELERATION_DEFAULT)
    right_top_motor.control.limits(acceleration=ARM_ACCELERATION_DEFAULT)


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


def drive_until_white_line(drive_base, left_color_sensor, right_color_sensor, distance, speed):
    # Like drive_base.straight(distance), but stops when either sensor sees white.
    # Returns True if it found white, False if not.
    drive_base.settings(straight_speed=speed)
    start = drive_base.distance()
    drive_base.straight(distance, wait=False)
    print_timer = StopWatch()
    while not drive_base.done():
        left = left_color_sensor.reflection()
        right = right_color_sensor.reflection()
        if PRINT_DEBUG_LINE_SENSOR_READINGS and print_timer.time() >= 50:
            print_timer.reset()
            print("Reflection left/right:", left, right, "at mm:", abs(drive_base.distance() - start))
        if left >= WHITE_LINE_MIN_REFLECTION or right >= WHITE_LINE_MIN_REFLECTION:
            drive_base.brake()
            print(f"White line! Reflection left/right: {left} {right} at mm: {abs(drive_base.distance() - start)} (before the max of {abs(distance)})")
            return True
        if drive_base.stalled():
            drive_base.stop()
            break
        wait(10)
    print("No white line found")
    return False


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


def move_arm_degrees(left_top_motor, right_top_motor, arm_degrees, arm_speed, blocking=True):
    # Moves the arm by arm_degrees (+ = up, - = down) at arm_speed (arm deg/s).
    # Both measured at the arm, not the motor.
    # blocking=True waits until done (and stops if stuck).
    # blocking=False starts the move and goes right on to the next line (e.g. to drive at the same time).
    motor_speed = arm_speed * ARM_GEAR_RATIO
    motor_degrees = arm_degrees * ARM_GEAR_RATIO
    if blocking:
        arm_until_done_or_stalled(left_top_motor, right_top_motor, motor_speed, motor_degrees)
    else:
        left_top_motor.run_angle(motor_speed, motor_degrees, wait=False)
        right_top_motor.run_angle(motor_speed, motor_degrees, wait=False)

