from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()

while True:
    print()
    print("Make a selection")
    print("1. Forward back")
    print("-1. Exit")
    selection = int(input("Selection: "))
    if selection == -1:
        break
    if selection == 1:
        print("Do a forward back")