# Remote Control Mode — Planning

## Status

**Implemented** (2026-08-31, revised 2026-09-01): `remote_protocol.py`,
`rosie_remote.py`, `rosie_rover.py`'s arm motors
(`left_top_motor`/`right_top_motor`), and `master_program.py`'s
`handle_remote()`. Migrated from `hub.ble`/`PrimeHub(observe_channels=...)`
to `pybricks.messaging.BLERadio` after the hub's firmware flagged the old
approach as moved (see "Communication" below). Tilt signs and the knob's
absolute-position calibration have both been confirmed on real hardware
(see "Tilt calibration" and "Knob calibration" below) by jury-rigging the
robot's own hub as a stand-in for the remote. The force-sensor-based mode
switch and per-motor lock were dropped in favor of a held LEFT button —
`rosie_remote.py` now needs no sensor beyond the knob motor, so it's fully
testable on a single hub. **Still not tested**: actual driving/arm movement
from a live remote, and BLE range/latency with two real hubs — needs the
second hub actually built.

## Goal

`master_program.py` runs in two modes on one file:
- **Mission mode**: number selector + CENTER launches `m<N>.run(robot)`
  (unchanged from before).
- **Remote control mode**: active *whenever a mission isn't currently
  running* — i.e. it runs concurrently with the selector loop, not as a
  separate menu state. The moment CENTER launches a mission, the remote is
  ignored (the loop is blocked inside the mission's `run()` call and never
  calls `handle_remote()` again until the mission returns).

Purpose: testing physical attachments and driver practice, **not**
competition runs (FLL matches are autonomous). `IS_REMOTE_ENABLED` in
`master_program.py` is the kill switch — set to `False` before competition
day.

## Hardware roles

- **Robot hub** ("Rosie Rover"): owns the drive base (Ports B/D) and the
  arm motors `left_top_motor`/`right_top_motor` (Ports C/E, confirmed
  permanent — they're in `RosieRover.__init__` now). Only ever receives
  commands, never broadcasts.
- **Remote hub** ("Rosie Remote", not yet built): held in two hands, big
  CENTER button near the driver's right thumb, BLUETOOTH button toward the
  front-left corner. Owns:
  - One large motor on **Port A**, used purely as a hand-turned dial (never
    driven) — the overall speed/power knob.
  - The hub's own **IMU** (tilt), used for two different things depending
    on mode (see below).
  - The hub's own **LEFT button** — held down = switch to attachment-control
    mode (released = drive mode). No force sensor needed (design changed
    2026-09-01, see "Attachment mode" below — originally planned a force
    sensor pushbutton plus per-motor locking via LEFT/RIGHT, dropped once
    it became clear the two arm motors should just always move together).

## Communication: BLE broadcast/observe via `BLERadio`

Modern connectionless API for Powered Up hubs (PrimeHub included) — **not**
the older EV3-specific `BluetoothMailboxServer`/`Client`.

**API history, so this doesn't get re-litigated**: this started as
`PrimeHub(broadcast_channel=N, observe_channels=[M, ...])` +
`hub.ble.broadcast()`/`hub.ble.observe()`, which is what's documented on
`docs.pybricks.com` and matches our local `pybricks` pip package (still
4.0.0 stable as of 2026-08-31). Then the actual hub printed a runtime
deprecation notice on boot ("Hub messaging has been moved..."), because
**the hub's firmware is running ahead of our local pip package** — the
pybricks 4.0.0b11 changelog confirms: "Moved BLE broadcasting and observing
to `pybricks.messaging.BLERadio` instead of an object on each hub." So the
firmware itself is the more current source of truth here, not the stable
docs site. Migrated (2026-08-31) to match:
```python
from pybricks.messaging import BLERadio
radio = BLERadio(broadcast_channel, observe_channels)
```
- `PrimeHub()` no longer takes `broadcast_channel`/`observe_channels` — a
  separate `BLERadio` object owns that now (`RosieRover.radio`,
  `rosie_remote.py`'s module-level `radio`).
- `radio.broadcast(data)` / `radio.observe(channel)` — same semantics as
  the old `hub.ble` methods (this was a move, not a redesign, per the
  changelog wording): ~26 byte payload limit, ~10Hz effective update rate
  (broadcasts go out every ~100ms regardless of call frequency), no
  pairing/naming needed.
- `remote_protocol.py` now has two channel constants: `REMOTE_BROADCAST_CHANNEL = 1`
  (remote → robot, the one that matters today) and
  `ROBOT_BROADCAST_CHANNEL = 2` (robot's own channel, required by the
  `BLERadio` constructor even though the robot doesn't broadcast anything
  yet — reserved for future status-back-to-remote use).
- **Lesson for future debugging**: when something the docs say should work
  doesn't match what the hub actually does, the hub's own runtime error
  text is more current than `docs.pybricks.com` or our local pip package —
  firmware and the PC-side `pybricks` package can drift apart in either
  direction.

**Wire format** (`remote_protocol.py` holds the shared constants so both
sides can't drift out of sync):
```python
(mode, speed_pct, pitch, roll)
```
- `mode`: `MODE_DRIVE` (0) or `MODE_ATTACHMENT` (1), from whether LEFT is
  currently held on the remote.
- `speed_pct`: 0–100, from the Port A knob (absolute position from its
  physical zero dot — see "Knob calibration" below).
- `pitch`, `roll`: raw degrees from `hub.imu.tilt()` on the remote.

(No `lock` field anymore — dropped along with the force sensor design, see
"Attachment mode" below.)

## Drive mode (mode == MODE_DRIVE)

Remote hub held like a joystick:
- Tip forward/back (pitch) → drive forward/backward.
- Tip left/right (roll) → turn in place (spin) when flat, or arc when
  combined with forward/back tilt.
- Fully analog: `MAX_TILT_DEG = 45` in `master_program.py` is the tilt
  angle treated as "full power" in either axis; `speed_pct` from the knob
  scales the ceiling (`MAX_DRIVE_SPEED_MMSEC = 500`,
  `MAX_TURN_RATE_DEGSEC = 200`) on top of that. Both are guesses — tune
  once the remote exists.
- Implemented as `robot.drive_base.drive(speed, turn_rate)` every loop
  tick — continuous, non-blocking, exactly the joystick feel wanted.

## Attachment mode (mode == MODE_ATTACHMENT)

Entered by holding **LEFT** on the remote (checked live every loop tick —
not a toggle, mode reverts to drive the instant LEFT is released). Same
IMU, repurposed: only pitch matters (roll ignored), tip forward/back drives
`left_top_motor`/`right_top_motor` (Ports C/E) together via open-loop
`motor.dc(pct)`, scaled by `MAX_ARM_DUTY_PCT = 70` and the same knob
`speed_pct`.

**Design changed 2026-09-01**: originally planned a force sensor as a
pushbutton for the mode switch, plus using the remote's LEFT/RIGHT buttons
to lock one arm motor stationary so the other could move independently.
Dropped both — decided the two arm motors should always move together (no
independent control needed), which meant the force sensor wasn't needed
either; holding the hub's own LEFT button is simpler and doesn't need extra
hardware. This also means `rosie_remote.py` is now fully testable without
any spare sensor at all — everything it needs (a large motor, the hub's own
buttons and IMU) already exists in one form or another.

Reference: the Blocks program you tested standalone (two motors, opposite
`Direction` settings so one command spins both the same physical way,
bang-bang via `Button.LEFT`/`RIGHT` and `dc(±20)`) confirmed the mechanism
and which ports/directions to use. That local-button version isn't part of
this repo — the mechanism itself (ports C/E, opposite directions) carried
over into `RosieRover`, but the *input* now comes from the remote's tilt
instead of local buttons.

## Remote's own display: ball (drive) / bar (attachment)

The remote shows live visual feedback on its own 5x5 display, separate
from anything the robot shows:
- **Drive mode**: a single lit pixel — "ball on a plane" — at
  `(row, col) = (2 + tilt_side*2, 2 + tilt_forward*2)`, using the same
  `tilt_forward`/`tilt_side` sign convention as the robot's
  `handle_remote()` (pitch → column: forward=4, backward=0; roll → row:
  left=0, right=4; center=(2,2) when flat). Verified against three
  hand-specified examples (forward-only, left-only, forward+left) —
  matched exactly.
- **Attachment mode**: a full vertical bar instead of a dot (roll doesn't
  matter here since both arm motors always move together) — same column
  math, every row lit in that column.

## Knob calibration (resolved 2026-08-31)

Learned that the large motor has a physical dot marking its true absolute
zero position, which the motor remembers across power cycles — so
`rosie_remote.py` deliberately does **not** call `reset_angle(0)` anymore
(that would have redefined "50% power" to wherever the knob happened to be
at boot, which isn't what we want). Measured: the dot position (angle 0) is
50% power, -90° from the dot is 0%, +90° is 100%. `KNOB_MAX_ANGLE` updated
from an initial guess of 180 to the confirmed **90**.

## Mode switching in `master_program.py`

Resolved: no dedicated button or reserved mission number needed.
`handle_remote()` runs unconditionally at the top of the existing selector
`while True` loop (guarded only by `IS_REMOTE_ENABLED`), so it's live the
entire time you're sitting in "pick a mission" mode, and automatically
paused the instant a mission starts running (the loop blocks inside
`run_mission(robot)`).

## Failsafe

If `radio.observe()` returns `None` (remote off, out of range, or never
started broadcasting), `handle_remote()` immediately calls
`robot.drive_base.stop()` and zeroes both arm motors. This relies on
`observe()`'s own documented staleness handling rather than a hand-rolled
timer — good enough for now since there's no hardware yet to tune a real
timeout against. Revisit if `observe()` turns out to hang onto stale data
longer than expected once both hubs exist.

Also handled: switching modes doesn't leave the *other* mode's motors
running — entering `MODE_DRIVE` explicitly zeroes the arm motors, entering
`MODE_ATTACHMENT` explicitly calls `drive_base.stop()`.

## Units question (asked, answered)

Pybricks has no inches mode — `DriveBase`/`Motor` distances and speeds are
always mm / mm/s (matches `wheel_diameter`/`axle_track` being given in mm
in `rosie_rover.py`). If thinking in inches is easier when writing mission
code, define a small helper (e.g. `def inches(n): return n * 25.4`) and
call `driveForDistance`-style methods with `inches(4)` etc. — not added
anywhere yet since nothing has asked for it.

## Tilt calibration (resolved 2026-08-31)

Tested by temporarily running a diagnostic version of `rosie_remote.py` on
the robot's own hub (no second hub needed — pure IMU test, Port A had a
spare large motor standing in for the knob, force sensor skipped since none
was on hand). Held flat, buttons up, CENTER toward right thumb — exactly
the intended remote grip. Raw `hub.imu.tilt()` readings:

| Pose | pitch | roll |
|---|---|---|
| Hold flat | 1.08 | -0.58 |
| Tip full forward | **-49.85** | -0.81 |
| Tip full backward | **+54.24** | -1.29 |
| Tip full left | 4.14 | **+45.60** |
| Tip full right | -1.22 | **-46.52** |

**Conclusions:**
- `top_side=Axis.Z, front_side=-Axis.Y` is correct — cross-axis leakage is
  small (≤5°) in both directions, confirming pitch cleanly tracks
  forward/back and roll cleanly tracks left/right for this grip. No change
  needed there.
- **Signs are inverted** relative to what `drive_base.drive(speed,
  turn_rate)` wants (positive speed = forward, positive turn_rate =
  clockwise/right): forward tilt gives *negative* pitch, left tilt gives
  *positive* roll. Fixed in `master_program.py`'s `handle_remote()` by
  negating both: `tilt_forward = -pitch / MAX_TILT_DEG`,
  `tilt_side = -roll / MAX_TILT_DEG`.
- `MAX_TILT_DEG = 45` confirmed as a good threshold — full tips measured
  46–54°, so 45° gives a little headroom before max power, no strain
  needed to hit it.
- Also noted: `hub.imu.tilt()` returns floats on this firmware, not the
  ints the docs describe (another docs/firmware mismatch, harmless here
  since the math doesn't care).

## Open questions still remaining

1. **`MAX_DRIVE_SPEED_MMSEC`, `MAX_TURN_RATE_DEGSEC`, `MAX_ARM_DUTY_PCT`**
   are still guesses pending a real drive test (tilt signs/threshold and
   the knob are now confirmed, per above, but these haven't been driven
   yet — needs the robot free to actually move, and BLE range/latency
   between two real hubs hasn't been tested at all).
2. Attachment mode (`Button.LEFT` held → arm control) is implemented but
   untested end-to-end — the diagnostic run only exercised drive-mode IMU
   values.

## Phased implementation

1. ~~Add `left_top_motor`/`right_top_motor` to `RosieRover`.~~ Done
   (renamed from `left_top`/`right_top` 2026-09-01).
2. ~~Write `rosie_remote.py` (broadcast-only, no robot-side reaction yet
   needed to test in isolation with `print()`).~~ Done.
3. ~~Add `handle_remote()` to `master_program.py`.~~ Done.
4. ~~Add the failsafe (`observe()` returns `None` → stop everything).~~ Done.
5. ~~Confirm tilt signs and `MAX_TILT_DEG`.~~ Done, see "Tilt calibration"
   above.
6. ~~Confirm knob calibration.~~ Done, see "Knob calibration" above.
7. ~~Drop the force sensor design; switch attachment mode to a held LEFT
   button.~~ Done 2026-09-01 — `rosie_remote.py` is now fully testable on
   a single hub with just a spare large motor, no other sensors needed.
8. **Next**: build the second hub for real (knob motor permanently
   mounted), then field-test actual driving and attachment-mode control,
   and retune the remaining speed constants.
