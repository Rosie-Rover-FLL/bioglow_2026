# Rosie Robotics
# Team #75872

Pybricks code for the 2026 FLL Bioglow season.

## Computer Setup

The hubs themselves already have Pybricks firmware installed — nothing to
do there. To use this code from your own computer:

1. Install the VS Code extension **"VS Code Keybindings for Pybricks"** by
   Skip Morrow — this is what makes the keyboard shortcuts below work.
2. Install the Python packages listed in `requirements.txt` (a virtual
   environment is recommended rather than installing them system-wide).

## Quick reference

### Keyboard shortcuts (pushing code to a hub)

These come from the "VS Code Keybindings for Pybricks" extension, and
shell out to tasks defined in `.vscode/tasks.json`.

| Shortcut | Pushes | To which hub |
|---|---|---|
| `Ctrl+L` | whatever file is currently open | the default hub (`fllRobotName` in `.vscode/settings.json`, currently "Rosie Rover") |
| `Ctrl+Shift+L` | always `rosie_rover_main.py`, no matter what's open | the default hub |
| `Ctrl+Alt+L` | whatever file is currently open | asks you to pick "Rosie Rover" or "Rosie Remote" from a dropdown each time |
| `Ctrl+Shift+Alt+L` | always `rosie_rover_main.py`, no matter what's open | asks you to pick from the same dropdown |

### Stopping a program

Both hubs deliberately disable the normal "press CENTER to stop" behavior,
since CENTER has another job on each of them (launching missions on the
robot; something coming soon on the remote). To stop either one:

**Hold CENTER + BLUETOOTH together.**

### Mission `00` = remote control

On the robot, dialing the mission-number display down to `00` hands
control to a second hub (see "Rosie Remote" below) — no CENTER press
needed, it's live the instant the display reads `00`. Dial to any other
number and the remote is completely ignored, so it can't nudge the robot
while it's being placed by hand for a mission.

## Hardware — port connections and hub orientation

### Rosie Rover (the robot)

| Port | Device | Attribute in `RosieRover` | Notes |
|---|---|---|---|
| A | Color sensor | `right_color_sensor` | |
| B | Large motor | `right_wheel` | `Direction.CLOCKWISE` |
| C | Large motor | `left_top_motor` | `Direction.CLOCKWISE` — arm/lift |
| D | Large motor | `left_wheel` | `Direction.COUNTERCLOCKWISE` |
| E | Large motor | `right_top_motor` | `Direction.COUNTERCLOCKWISE` — arm/lift |
| F | Color sensor | `left_color_sensor` | |

Hub orientation: `top_side=Axis.Z, front_side=-Axis.Y` — mounted with the
screen/buttons facing up.

Drive base: 85mm wheel diameter, 110mm axle track (`left_wheel`,
`right_wheel`).

### Rosie Remote

| Port | Device | Notes |
|---|---|---|
| A | Large motor | Speed knob — turned by hand, never driven. Has a physical dot marking its true zero; that position is 50% power, ±90° reaches 0%/100%. |

Hub orientation: same as the robot — `top_side=Axis.Z, front_side=-Axis.Y`
— held flat in two hands, buttons facing up, CENTER button toward the
driver's right thumb, BLUETOOTH button toward the front-left corner.

## File layout at a glance

- `rosie_rover_main.py` — the main program that runs on the robot.
- `rosie_rover.py` — the `RosieRover` class (the robot's hardware setup).
- `rosie_remote_main.py` — the main program that runs on the remote.
- `remote_protocol.py` — shared constants so the two main programs agree
  with each other.
