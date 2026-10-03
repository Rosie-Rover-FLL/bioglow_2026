QUIT = 1
FORWARD = 2
SPIN = 3
DISTANCES = [10, 20, 30, 50, 100]
DEGREES = [10, 20, 30, 45, 90]

from pybricks.tools import wait

def adjust(robot, mm_to_delay=1000):
    # Function to adjust the position of Rosie
    print("Adjusting Rosie's position...")
    while True:
        command, distance, direction = choose_operation()
        if command == QUIT:
            break
        wait(mm_to_delay)
        run_operation(robot, command, distance, direction)
    wait(mm_to_delay)

def choose_operation(robot):
    command = select_choice(robot, "C", 0.6, 3)
    distance = select_choice(robot, "D", 0.7, 5)
    direction = select_choice(robot, ">", 0.8, 2) * 2 - 3  # Convert to -1 or 1
    return command, distance, direction

def select_choice(robot, label, pitch, n_choices):
    robot.hub.display.text(label)
    result = 0
    while True:
        if robot.hub.buttons.left.is_pressed():
            while True:
                if robot.hub.buttons.left.is_released():
                    break
        elif robot.hub.buttons.right.is_pressed():
            while True:
                if robot.hub.buttons.right.is_released():
                    break
            result = (result + 1) % n_choices
            for _ in range(result + 1):
                wait(0.1)
                robot.hub.speaker.beep(pitch=pitch)
    return result + 1

def run_operation(robot, command, distance, direction):
    if command == FORWARD:
        real_distance = DISTANCES[distance - 1] * MM_PER_INCH
        robot.drive_base.straight(real_distance * direction)
    elif command == SPIN:
        real_degrees = DEGREES[distance - 1]
        robot.spin(real_degrees * direction)