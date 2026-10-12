from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait


def setup():
    left_wheel = Motor(Port.D, Direction.COUNTERCLOCKWISE)
    right_wheel = Motor(Port.B, Direction.CLOCKWISE)
    left_top_motor = Motor(Port.C, Direction.CLOCKWISE)
    right_top_motor = Motor(Port.E, Direction.COUNTERCLOCKWISE)
    left_color_sensor = ColorSensor(Port.F)
    right_color_sensor = ColorSensor(Port.A)
    prime_hub = PrimeHub(top_side=Axis.Z, front_side=-Axis.Y)
    drive_base = DriveBase(left_wheel, right_wheel, 85, 110)
    return (
        left_top_motor,
        right_top_motor,
        left_color_sensor,
        right_color_sensor,
        prime_hub,
        drive_base,
    )


def print_battery(prime_hub):
    print(f"Battery voltage: {prime_hub.battery.voltage()} mV")


def straight_until_done_or_stalled(drive_base, distance):
    # Drive straight, but give up early if the robot gets stuck (stalls).
    drive_base.straight(distance, wait=False)
    while not drive_base.done():
        if drive_base.stalled():
            drive_base.stop()
            break
        wait(10)


def arm_until_done_or_stalled(left_top_motor, right_top_motor, speed, angle):
    # Turn both arm motors at the same time. The two motors work together,
    # so if either one gets stuck (stalls), stop both and give up early.
    left_top_motor.run_angle(speed, angle, wait=False)
    right_top_motor.run_angle(speed, angle, wait=False)
    while not (left_top_motor.done() and right_top_motor.done()):
        if left_top_motor.stalled() or right_top_motor.stalled():
            left_top_motor.stop()
            right_top_motor.stop()
            break
        wait(10)
