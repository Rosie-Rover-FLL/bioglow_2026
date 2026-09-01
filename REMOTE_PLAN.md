# Remote Control Mode — Planning

## Status

**Implemented** (2026-08-31): `remote_protocol.py`, `rosie_remote.py`,
`rosie_rover.py`'s arm motors, and `master_program.py`'s `handle_remote()`.
Testable today on the robot side (mission mode unaffected; remote branch
safely no-ops since no second hub exists yet to broadcast). **Not yet
tested** on real remote hardware — signs/directions on the IMU tilt and the
exact feel of the knob/tilt scaling will need tuning once the second hub is
built. Migrated same day from `hub.ble`/`PrimeHub(observe_channels=...)` to
`pybricks.messaging.BLERadio` after the actual hub's firmware flagged the
old approach as moved (see "Communication" section below) — this part
*was* verified against real hardware, since it's just `RosieRover`
construction, no second hub needed.

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
  arm motors `left_top`/`right_top` (Ports C/E, confirmed permanent —
  they're in `RosieRover.__init__` now). Only ever receives commands, never
  broadcasts.
- **Remote hub** ("Rosie Remote", not yet built): held in two hands, big
  CENTER button near the driver's right thumb, BLUETOOTH button toward the
  front-left corner. Owns:
  - One large motor on **Port A**, used purely as a hand-turned dial (never
    driven) — the overall speed/power knob.
  - The hub's own **IMU** (tilt), used for two different things depending
    on mode (see below).
  - A **force sensor on Port B**, used as a pushbutton — held down = switch
    from drive mode to attachment-control mode.
  - The hub's own **LEFT/RIGHT buttons** — in attachment mode only, used to
    lock one arm motor stationary so the other can move independently.

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
(mode, speed_pct, pitch, roll, lock)
```
- `mode`: `MODE_DRIVE` (0) or `MODE_ATTACHMENT` (1), from the force sensor.
- `speed_pct`: 0–100, from the Port A knob (`50 + angle/180*50`, clamped —
  center of knob's travel = 50%, ±180° reaches 0%/100%).
- `pitch`, `roll`: raw degrees from `hub.imu.tilt()` on the remote.
- `lock`: `LOCK_NONE`/`LOCK_LEFT`/`LOCK_RIGHT`, only meaningful in
  attachment mode.

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

Same IMU, repurposed: only pitch matters (roll ignored), tip forward/back
drives `left_top`/`right_top` (Ports C/E) together via open-loop
`motor.dc(pct)`, scaled by `MAX_ARM_DUTY_PCT = 70` and the same knob
`speed_pct`. Holding the remote's LEFT button zeroes `left_top` (keeps C
stationary, only E moves); holding RIGHT zeroes `right_top` (keeps E
stationary, only C moves) — lets the two motors act independently instead
of always moving as a mirrored pair.

Reference: the Blocks program you tested standalone (two motors, opposite
`Direction` settings so one command spins both the same physical way,
bang-bang via `Button.LEFT`/`RIGHT` and `dc(±20)`) confirmed the mechanism
works and which ports/directions to use. That local-button version isn't
part of this repo — the mechanism itself (ports C/E, opposite directions)
carried over into `RosieRover`, but the *input* now comes from the remote's
tilt instead of local buttons.

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

1. **`MAX_DRIVE_SPEED_MMSEC`, `MAX_TURN_RATE_DEGSEC`, `MAX_ARM_DUTY_PCT`,
   `KNOB_MAX_ANGLE`** are still guesses pending a real drive test (tilt
   signs/threshold are now confirmed, per above, but these haven't been
   driven yet — needs the robot free to actually move).
2. Force sensor port (`Port.B` on the remote) is wired in code but
   untested — no force sensor available yet to confirm it physically.

## Phased implementation

1. ~~Add `left_top`/`right_top` to `RosieRover`.~~ Done.
2. ~~Write `rosie_remote.py` (broadcast-only, no robot-side reaction yet
   needed to test in isolation with `print()`).~~ Done, untested on
   hardware.
3. ~~Add `handle_remote()` to `master_program.py`.~~ Done.
4. ~~Add the failsafe (`observe()` returns `None` → stop everything).~~ Done.
5. ~~Confirm tilt signs and `MAX_TILT_DEG`.~~ Done, see "Tilt calibration"
   above.
6. **Next**: build the physical remote hub (with a real force sensor), then
   field-test and retune the remaining drive/arm speed constants.
