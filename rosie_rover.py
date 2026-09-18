from pybricks.hubs import PrimeHub
from pybricks.parameters import Axis, Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase


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
