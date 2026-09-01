from pybricks.hubs import PrimeHub
from pybricks.messaging import BLERadio
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase

from remote_protocol import REMOTE_BROADCAST_CHANNEL, ROBOT_BROADCAST_CHANNEL


class RosieRover:
    def __init__(self):
        self.left_wheel = Motor(Port.D, Direction.COUNTERCLOCKWISE)
        self.right_wheel = Motor(Port.B, Direction.CLOCKWISE)
        self.left_top_motor = Motor(Port.C, Direction.CLOCKWISE)
        self.right_top_motor = Motor(Port.E, Direction.COUNTERCLOCKWISE)
        self.left_color_sensor = ColorSensor(Port.F)
        self.right_color_sensor = ColorSensor(Port.A)
        self.prime_hub = PrimeHub()
        self.radio = BLERadio(ROBOT_BROADCAST_CHANNEL, [REMOTE_BROADCAST_CHANNEL])
        self.drive_base = DriveBase(self.left_wheel, self.right_wheel, 85, 110)

    def print_battery(self):
        print(f"Battery voltage: {self.prime_hub.battery.voltage()} mV")
