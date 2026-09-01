from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase

class RosieRover:
    def __init__(self):
        self.left_wheel = Motor(Port.D, Direction.CLOCKWISE)
        self.right_wheel = Motor(Port.B, Direction.COUNTERCLOCKWISE)
        self.prime_hub = PrimeHub()
        self.drive_base = DriveBase(self.left_wheel, self.right_wheel, 85, 110)

    def print_battery(self):
        print(f"Battery voltage: {self.prime_hub.battery.voltage()} mV")