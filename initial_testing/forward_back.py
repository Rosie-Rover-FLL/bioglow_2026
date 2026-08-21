from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

def main():
    motor = Motor(Port.C)

    motor.run(500)   # speed in degrees per second
    wait(1000)       # run for 1 second
    motor.stop()     # coast to a stop

main()