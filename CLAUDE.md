# Bioglow 2026 — Team Rosie Rover

## Big picture

This is a **First Lego League (FLL)** robotics team repo for the **Bioglow 2026**
season. Our team is **Rosie Rover**, a brand-new team. We bootstrapped our
approach by temporarily copying in a more experienced team's repo (**Team
24277**, https://github.com/FLL-Team-24277) to learn their patterns. Those
reference folders (`team_24277_code/`, `team_24277_vscode/`) have since been
deleted (2026-08-31) — everything worth keeping was folded into this file,
`requirements.txt`, and `help/`, with the rest intentionally left behind (see
"Patterns learned from Team 24277" below for what was absorbed).

- **Robot/hardware**: LEGO SPIKE Prime hub, driven with **Pybricks**
  (MicroPython-based firmware/API for LEGO hubs), not the stock LEGO
  Education software.
- **Roles**:
  - **Students** write mission code — one module per mission.
  - **Coach (David, the primary user of this assistant)** handles setup:
    repo scaffolding, VS Code config, the base robot driver class, the
    master program, and infrastructure so students can focus on mission
    logic.
- **Dev environment**: VS Code + a Python virtual environment (`.venv`,
  managed with `uv`). Programs are pushed to the hub over Bluetooth LE using
  `pybricksdev run ble --name "<hub name>" <file>`, wired up as VS Code tasks
  (see `.vscode/tasks.json`). The hub's BLE name is stored in
  `.vscode/settings.json` as `fllRobotName` (currently `"Rosie Rover"`).

## Repo layout

- `rosie_rover_main.py` — our top-level program that runs on the robot's
  hub, shows the mission-number selector, and launches the selected mission
  module. (Named `master_program.py` until 2026-09-01 — renamed alongside
  `rosie_remote.py` → `rosie_remote_main.py` so the two main programs are
  named as a matched pair, distinct from `rosie_rover.py` below.)
  **Quirk**: the `Ctrl+Shift+L` keybinding (from the
  `SkipMorrow.vs-code-keybindings-for-pybricks` extension) triggers a task
  by exact label text, which is baked into that extension — so
  `.vscode/tasks.json`'s "Run master_program.py on my robot" task label was
  deliberately left unchanged even though its `args` now push
  `rosie_rover_main.py`. The stale-looking label is intentional, not a bug.
- `rosie_rover.py` — plain functions, no class (changed 2026-09-18, was a
  `RosieRover` class before that): `setup()` builds the hub, drive motors,
  drive base, arm motors, and color sensors, and returns exactly six
  objects (`left_top_motor, right_top_motor, left_color_sensor,
  right_color_sensor, prime_hub, drive_base`); `print_battery(prime_hub)`
  and `straight_until_stalled(drive_base, distance)` are the other
  functions. No mission imports here, so both `rosie_rover_main.py` and
  mission files can import from it with zero circular-import risk.
- `m1.py`, `m2.py`, ... — one file per mission, each with a `run(left_top_motor,
  right_top_motor, left_color_sensor, right_color_sensor, prime_hub,
  drive_base)` function taking those same six params positionally (see
  "Mission module conversion workflow" below).
- `requirements.txt` — unpinned `pybricks`/`pybricksdev`; we deliberately
  track latest rather than pinning versions like Team 24277 did.
- `help/` — reference docs worth keeping long-term: `discovery.md` (why
  sharing mission code doesn't spoil FLL's Discovery core value) and
  `training_videos.md` (VS Code/git/Python onboarding videos). Both
  adapted/carried over from Team 24277 with attribution in the file.
- `initial_testing/` — early scratch experiments (keyboard driving, a basic
  menu, hello world). Nothing load-bearing here; safe to ignore/replace.

## Patterns learned from Team 24277 (to reuse/adapt, not copy verbatim)

### `BaseRobot` class (`base_robot.py`)
A wrapper class instantiated once (`br = BaseRobot()`) that owns the hub,
drive motors, attachment motors, `DriveBase`, and color sensor. It exposes
kid-friendly methods like `driveForDistance`, `driveForMillis`, `turnInPlace`,
`curve`, `moveLeftAttachmentMotorForDegrees`, `waitForForwardButton`, etc.
All speed/acceleration parameters are given as **percentages (1–100)** and
rescaled internally (see `utils.py`) to real Pybricks units — this keeps the
mission-writing API simple for students and keeps hardware tuning constants
in one place.

### Mission module convention
Each mission is its own `.py` file that defines:

```python
def Run(br: BaseRobot):
    ...mission steps...

if __name__ == "__main__":
    br = BaseRobot()
    Run(br)
```

The `if __name__ == "__main__"` block lets a student run **just their
mission** standalone while developing, without going through the master
program. The master program instead does `import mission_module` once up
top, then calls `mission_module.Run(br)` whenever that mission should run.

**Important Pybricks gotcha**: an `import` statement only executes a
module's top-level code the *first* time it's imported on a given hub boot,
even if you "import" it again later. This is why missions expose a callable
`Run(br)` function rather than relying on import-time side effects — it lets
the master program invoke the same mission multiple times if needed.

### Master program pattern
Team 24277's `master_program.py` imports all mission modules up front, then
loops: detect a selection signal (in their case, a color sensor reading +
which side of the table), and calls the matching `mission.Run(br)`.

### VS Code / pybricksdev workflow
- `.vscode/tasks.json` defines tasks like "Run on my robot" and "Run
  master_program.py on my robot", both shelling out to `pybricksdev run ble
  --name <fllRobotName> <file>`.
- `.vscode/settings.json` stores the hub's BLE name per-machine as
  `fllRobotName`.
- They also maintain custom code snippets (`dfd`, `dfm`, `tip`, `rmd`, `lmd`,
  `wfb`, `wbb`, etc.) as shorthand for common `BaseRobot` calls.

## Key Pybricks facts (verified against official docs)

- `hub.buttons.pressed()` returns a set of `Button` enum values:
  `Button.LEFT`, `Button.RIGHT`, `Button.CENTER`, `Button.BLUETOOTH`.
- **By default, pressing the CENTER button stops the running program.** This
  can be reassigned or disabled with
  `hub.system.set_stop_button(...)` (e.g. set it to
  `(Button.CENTER, Button.BLUETOOTH)` or `None`), after which `Button.CENTER`
  can be read like any other button in `hub.buttons.pressed()`. This matters
  for our plan since we want the center button to *launch* a program, not
  stop one.
- `hub.display.number(n)` shows an integer in the range **-99 to 99** (two
  digits); values outside that range show `>` or `<`. `hub.display.char()`
  shows a single letter/symbol. `hub.display.icon()` shows a custom 5x5
  Matrix.
- Pybricks also ships a built-in convenience, `hub_menu()` (from
  `pybricks.tools`), which shows a set of symbols and lets the user cycle
  through them with left/right and pick with center — useful prior art, but
  it cycles discrete symbols rather than an incrementing number, so we're
  building our own selector for the two-digit counter behavior we want.
- `hub.speaker.beep(frequency=500, duration=100)` and
  `hub.speaker.volume(pct)` (0-100) control the hub's built-in speaker.
- `StopWatch()` (from `pybricks.tools`) — `.time()` gives elapsed ms since
  creation, used for mission run-time reporting.
- **Docs vs. firmware can drift out of sync — trust the hub over the docs
  site.** Our local `pybricks` pip package is 4.0.0 stable and
  `docs.pybricks.com` still documents `hub.ble`/`PrimeHub(broadcast_channel=...)`
  for hub-to-hub messaging, but the *actual hub firmware* had already moved
  that to `pybricks.messaging.BLERadio` (confirmed via the pybricks
  4.0.0b11 changelog) and prints a runtime deprecation notice on boot
  telling you so. When something documented doesn't match what the hub
  actually does, believe the hub's own error text first.
- **MicroPython's compiler accepts less than CPython does — `python3 -c
  "import ast; ast.parse(...)"` is not a real syntax check for this
  project.** Found 2026-09-01: two adjacent f-string literals split across
  lines (`f"a {x}" \n f"b {y}"`, no `+`) parse fine under CPython's `ast`
  but `mpy-cross` rejects them with `SyntaxError: invalid syntax` — plain
  strings and a single f-string with a format spec are both fine, just not
  two f-strings placed next to each other. Caused a real deploy failure in
  `rosie_remote_main.py`'s status-print code (fixed by merging into one
  f-string). **To actually verify a file will run on the hub**, compile it
  with the real cross-compiler instead:
  `cat file.py | .venv/lib/python3.14/site-packages/mpy_cross_v6/mpy-cross - -s file.py -o /tmp/out.mpy`
  (exit code 0 = compiles; anything else prints the real MicroPython
  syntax error, unlike pybricksdev's own traceback which swallows it).

## Our robot & master program (implemented)

Instead of a `BaseRobot` god-class like Team 24277's, we don't have a robot
class at all (dropped 2026-09-18, was a `RosieRover` class before that) —
`rosie_rover.py`'s `setup()` function builds the hub, drive base
(`left_wheel`, `right_wheel`, `drive_base`), the arm motors
(`left_top_motor`/`right_top_motor` on Ports C/E), and two color sensors
(`left_color_sensor` on Port F, `right_color_sensor` on Port A), and
returns six plain objects rather than bundling them into an instance — see
the mission-conversion workflow below for how those get passed around.
All six hub ports are now in use (D/B drive, C/E arm, F/A color sensors) —
no ports free for ad-hoc bench testing of other parts (e.g. the remote's
knob code) without unplugging something.

**Why no class**: explicit team decision — mission functions take the six
values as plain positional parameters instead of one `robot` object with
attributes. `rosie_rover_main.py` unpacks `rosie_rover.setup()`'s return
tuple into six module-level names once at startup and uses them directly
(no `robot.` prefix anywhere in that file either) — `left_top_motor`,
`right_top_motor`, `left_color_sensor`, `right_color_sensor`, `prime_hub`,
`drive_base` is the canonical order everywhere: the function's return
tuple, every mission's `run(...)` signature, and every call site.

**Drive motor directions, confirmed on hardware (2026-09-01):**
`left_wheel = Motor(Port.D, Direction.COUNTERCLOCKWISE)`,
`right_wheel = Motor(Port.B, Direction.CLOCKWISE)`. The very first Blocks
export we converted into `m1.py`'s setup had these two **reversed**, which
we copied into `rosie_rover.py` without testing — that's why `m2.py` drove
backward. If `rosie_rover.py` is ever regenerated from a fresh Blocks
export, don't trust the export's directions blindly; verify against a real
`drive_base.straight()` test first.

**Hub orientation**: `prime_hub = PrimeHub(top_side=Axis.Z,
front_side=-Axis.Y)` (2026-09-01) — the hub is mounted on the robot the
same physical way the remote is held, so it uses the same orientation
config. This affects gyro-based heading correction during driving, not
just tilt reading (the robot doesn't read its own tilt).

`rosie_rover_main.py`:
- Calls `rosie_rover.setup()` once and unpacks the six values into
  module-level names; also builds its own `radio = BLERadio(...)`
  separately (not part of `setup()`'s six — missions never need it, only
  the remote-control code in this file does).
- Reassigns the stop button to `(Button.CENTER, Button.BLUETOOTH)` via
  `prime_hub.system.set_stop_button(...)` so CENTER is free to use as "run"
  instead of "stop".
- Shows a two-digit number on the hub display, starting at `1`.
- RIGHT increments the number, LEFT decrements it (wraps between 0 and 99).
  `0` is reserved for remote control — never map a mission to it.
- CENTER runs the mission mapped to the current number, via a `MISSIONS`
  dict (`{1: m1.run, ...}`) built from statically-imported mission modules.
  **Mission modules must be imported by literal name at the top of
  `rosie_rover_main.py`** (`import m1`, `import m2`, ...) — pybricksdev
  bundles files onto the hub by statically scanning for `import` statements,
  so a dynamically-computed import (e.g. `__import__(f"m{n}")`) would not
  get transferred to the hub.
- After a mission runs, the same number stays displayed so it can be rerun.
- If CENTER is pressed on a number with no mission mapped, the hub flashes a
  checkerboard pattern (and its inverse) on the 5x5 display for 0.5s each,
  then jumps to `max(MISSIONS)` — the highest mission number that actually
  exists.
- `rosie_rover.print_battery(prime_hub)` (prints `hub.battery.voltage()` in
  mV) is called once at program start and again right before each mission
  runs, so battery health is visible in the console both at boot and
  per-mission.
- Student-facing feedback: beeps and shows a right-pointing "play" triangle
  on the display while a mission runs (beeps again on completion), and
  prints `Starting Mission NN` / `Finished Mission NN, time X.X seconds`
  (via `StopWatch`) to the console for each run. `USE_LOW_VOLUME_BEEP`
  controls speaker volume (quiet for late-night testing vs. full volume).
  Prints an ASCII-art "ROSIE ROVER" banner at startup and "Goodbye" on
  shutdown (via `try`/`finally` around the main loop, since the loop itself
  never exits on its own — only the CENTER+BLUETOOTH stop signal ends it).
  The stop signal raises inside the loop rather than letting it finish
  normally, so the `finally` block also calls `stop_remote_motion()` before
  printing "Goodbye" — nothing guarantees the firmware stops
  actively-commanded motors on an interrupted (vs. normal) program exit.
- Also runs a **remote control mode**, driven by a second hub ("Rosie
  Remote") over BLE broadcast/observe — but only while the display reads
  mission `0`; any other number and it's completely ignored (no separate
  on/off flag needed — dialing away from `0` is the off switch). This is
  for driver practice/attachment testing only, not competition runs.
  Leaving mission `0` (via any of RIGHT/LEFT/CENTER, or the program
  stopping entirely) calls `stop_remote_motion()` so nothing keeps moving
  from a stale remote command. Related files: `remote_protocol.py` (shared
  wire-format constants, including the drive/arm speed ceilings so the
  remote's own status print stays consistent with what the robot actually
  does), `rosie_remote_main.py` (the second hub's program).

### Things learned from Team 24277 but deliberately *not* carried over
- **No auto git-pull automation** (they had a "pull on VS Code folder open"
  task plus a Windows Task Scheduler daily pull). Decided against it —
  unnecessary complexity for this team.
- **No `.vscode/extensions.json`** recommended-extensions list — not needed
  right now.
- **Coach diagnostic scripts** (color sensor calibration, motor
  stall/load tuning, battery monitor loop) — the *pattern* is worth knowing
  about but their actual code wasn't copied in. Recreate a small standalone
  script in that style if/when we add a color sensor or need to tune
  stall-based attachment moves.

## Mission module conversion workflow

Missions start as LEGO SPIKE **Word Blocks** programs. When exported, they
come as a text blob containing a `# pybricks blocks file: {...}` JSON
comment (the Blocks editor's internal representation, safe to ignore/keep
as a comment) followed by the generated Python, e.g.:

```python
# pybricks blocks file: {...}
from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase

# Set up.
left_wheel = Motor(Port.D, Direction.CLOCKWISE)
right_wheel = Motor(Port.B, Direction.COUNTERCLOCKWISE)
prime_hub = PrimeHub()
drive_base = DriveBase(left_wheel, right_wheel, 85, 110)

# The main program starts here.
drive_base.straight(170)
drive_base.turn(90)
drive_base.straight(150)
```

The coach (David) converts this into an `m<N>.py` mission module by hand:
- The setup block (motors, hub, drive base, sensors) is expected to already
  be covered by `rosie_rover.py`'s `setup()`. For now every mission shares
  the same setup, so nothing mission-specific needs to be added there —
  but as missions need different hardware/setup, we'll need to figure out
  how to share/extend that.
- The "main program starts here" block becomes the body of a `run(...)`
  function taking the six `setup()` values as plain parameters — bare
  variable names (`drive_base`, ...) in the Blocks export already match
  the parameter names directly, no `robot.` prefix needed (that pattern
  was dropped 2026-09-18 along with the `RosieRover` class).
- Every mission file is just a `run(...)` function — no `if __name__ ==
  "__main__"` standalone block (removed 2026-09-18 to keep the m files
  simple; missions are run through `rosie_rover_main.py` instead). The only
  import a mission should need is a shared helper, e.g.
  `from rosie_rover import straight_until_stalled` (added 2026-10-02).
  **Why the helper exists**: `DriveBase.straight()` has no stop-on-stall
  option (checked against pybricks source + changelog, 2026-10-02), and
  `Motor.run_until_stalled()` is per-motor and blocking, so using it on
  the two wheels would turn them one after the other instead of driving
  straight. The helper starts `straight(..., wait=False)` and polls
  `drive_base.stalled()`:

```python
def run(left_top_motor, right_top_motor, left_color_sensor, right_color_sensor, prime_hub, drive_base):
    ...mission steps, using drive_base etc. directly...
```

Note this repo uses lowercase `run(...)` (not Team 24277's `Run(br)`) —
keep that consistent across all mission modules. Parameter order is always
`left_top_motor, right_top_motor, left_color_sensor, right_color_sensor,
prime_hub, drive_base`, matching `rosie_rover.setup()`'s return tuple
exactly — a mission that only uses `drive_base` still declares all six
parameters (unused ones just sit there; pyright/pylance will flag them as
unused, that's expected and fine).

`m1.py` is the first mission built this way. To add `m2`, `m3`, etc.:
repeat the conversion above, then in `rosie_rover_main.py` add `import m2`
and add `2: m2.run` to the `MISSIONS` dict.
