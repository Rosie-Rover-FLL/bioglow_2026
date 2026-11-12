"""Rosie Rover simulator -- watch a mission drive on the field.

    .venv/bin/python simulator/simulator.py 17
    .venv/bin/python simulator/simulator.py 17 --gif m17.gif
    .venv/bin/python simulator/simulator.py 2 --start 60 13 90

Runs the REAL mission file (m17.py etc.) with a pretend robot: fake
drive_base / motors / hub that just do math on a simulated clock instead of
moving anything. Then it animates the result on field.jpg using robot.png.

Just for fun and rough planning -- the real robot slips, drifts, and bumps
into things. The simulator does none of that (nothing ever stalls).

Field coordinates (same as documents/field_planning/README.md):
  x = cm from the left (red) wall, y = cm from the south wall,
  heading 0 = east (toward the blue launch area), 90 = north.
"""

import argparse
import math
import os
import sys
import types

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# --- Field and robot measurements -------------------------------------------

FIELD_W_CM = 200
FIELD_H_CM = 114.3
# Where the field edges are inside field.jpg (measured from its red grid).
FIELD_IMG_LEFT, FIELD_IMG_RIGHT = 9.5, 1360.5
FIELD_IMG_TOP, FIELD_IMG_BOTTOM = 5.5, 774.5

# robot.png is a top view, front of the robot at the top of the picture.
# Size from the hub in the photo (a SPIKE Prime hub is 8.8 cm wide).
ROBOT_W_CM = 17.2
ROBOT_L_CM = 26.2
# Where the drive wheels are, measured from the BACK of the robot. Pybricks'
# x/y is the point halfway between the two drive wheels. Guess: the middle.
AXLE_FROM_BACK_CM = ROBOT_L_CM / 2

# Start poses: (x cm, y cm, heading deg). Measure on the real table and add
# more here as we figure them out. Anything missing uses DEFAULT_START.
START_POSES = {
    # Estimated from the robot photos in "Biglow missions Rosie Robotics
    # Team #75872.pdf" plus what each mission's code does -- rough, so
    # measure on the real table and fix these when you can.
    # Left launch area, side against the south wall, facing west (backs east first).
    1: (33, ROBOT_W_CM / 2, 180),
    # Left launch area, pointing out from the corner at the Exploding Seeds.
    2: (27, 23.6, 41),
    # Against the left wall, facing south (backs north to the rock first).
    3: (ROBOT_W_CM / 2 + 0.5, 30, 270),
    # Right launch area, back toward the corner, pointing out past the arc
    # (northwest). 135 lines the slow push up with the Leafcutter model.
    6: (167, 12, 135),
    # From the orange box sketch: back on the south wall, facing north.
    7: (176.5, AXLE_FROM_BACK_CM, 90),
    # Right launch area, left of the BIOGLOW logo, angled up and to the left.
    13: (163, 19, 120),
    # Left launch area, front against the south wall, facing south (backs north first).
    15: (37, ROBOT_L_CM - AXLE_FROM_BACK_CM, 270),
    # Back against the south wall in the right launch area, facing north.
    17: (167.3, AXLE_FROM_BACK_CM, 90),
    # Left launch area, aimed 20 degrees toward the far wall.
    16: (14, 16, 20),
}
DEFAULT_START = (30, AXLE_FROM_BACK_CM, 90)  # left launch area, back on the wall

MATCH_LIMIT_MS = 150_000  # a whole FLL match; stops runaway "wait forever" loops

# Pybricks limits for our motors (see CLAUDE.md "Pybricks drive defaults").
MAX_STRAIGHT_SPEED = 742  # mm/s
MAX_TURN_RATE = 773  # deg/s
MOTOR_MAX_DEG_S = 1000


# --- Simulated clock --------------------------------------------------------

class SimTimeout(Exception):
    pass


class Clock:
    def __init__(self):
        self.ms = 0.0
        self.log = []  # (time ms, "command text") for the on-screen readout

    def advance_to(self, ms):
        if ms > self.ms:
            self.ms = ms
        if self.ms > MATCH_LIMIT_MS:
            raise SimTimeout("mission ran longer than a whole match (2.5 min)")

    def note(self, text):
        self.log.append((self.ms, text))


clock = Clock()


def fmt_call(name, *args, **kwargs):
    parts = [repr(a) if isinstance(a, str) else f"{a:g}" if isinstance(a, float) else str(a) for a in args]
    for k, v in kwargs.items():
        if k == "wait" and v is True:
            continue
        parts.append(f"{k}={getattr(v, 'name', v)}")
    return f"{name}({', '.join(parts)})"


# --- Speed profiles ---------------------------------------------------------

class Profile:
    """Trapezoid speed profile over a distance D (mm or deg), always >= 0.

    Speeds up from v0 at `acc`, cruises at vmax, slows to vend at `dec`.
    """

    def __init__(self, D, vmax, acc, dec, v0=0.0, vend=0.0):
        D = abs(D)
        vmax = max(abs(vmax), 1e-6)
        v0 = min(abs(v0), vmax)
        vend = min(abs(vend), vmax)
        self.D = D
        if D == 0:
            self.v0 = self.vp = self.vend = v0
            self.t1 = self.t2 = self.t3 = 0.0
            self.acc = self.dec = 1.0
            self.T = 0.0
            return
        da = (vmax ** 2 - v0 ** 2) / (2 * acc)
        dd = (vmax ** 2 - vend ** 2) / (2 * dec)
        if da + dd <= D:
            vp = vmax
        else:
            vp = math.sqrt((2 * acc * dec * D + dec * v0 ** 2 + acc * vend ** 2) / (acc + dec))
            if vp < vend:  # too short to even reach vend: speed up the whole way
                vp = vend = math.sqrt(v0 ** 2 + 2 * acc * D)
            if vp < v0:  # coming in too fast: slow down the whole way
                vp = v0
                dec = max((v0 ** 2 - vend ** 2) / (2 * D), 1e-6)
        self.v0, self.vp, self.vend, self.acc, self.dec = v0, vp, vend, acc, dec
        self.t1 = (vp - v0) / acc
        self.t3 = (vp - vend) / dec
        cruise = D - (vp ** 2 - v0 ** 2) / (2 * acc) - (vp ** 2 - vend ** 2) / (2 * dec)
        self.t2 = max(cruise, 0.0) / vp
        self.T = self.t1 + self.t2 + self.t3  # seconds

    def at(self, t):
        """(distance so far, speed) after t seconds."""
        t = max(0.0, min(t, self.T))
        if t <= self.t1:
            return self.v0 * t + 0.5 * self.acc * t * t, self.v0 + self.acc * t
        s1 = self.v0 * self.t1 + 0.5 * self.acc * self.t1 ** 2
        if t <= self.t1 + self.t2:
            return s1 + self.vp * (t - self.t1), self.vp
        tt = t - self.t1 - self.t2
        s2 = s1 + self.vp * self.t2
        return min(s2 + self.vp * tt - 0.5 * self.dec * tt * tt, self.D), self.vp - self.dec * tt


# --- Fake DriveBase ---------------------------------------------------------

def _stop_name(then):
    return getattr(then, "name", str(then))


class Segment:
    """One drive_base move. pose(t) works for t from start to end (ms)."""

    def __init__(self, start_ms, pose0, kind, profile=None, sign=1, radius_mm=None,
                 speed=0.0, turn_rate=0.0, linear=True):
        self.start = start_ms
        self.pose0 = pose0
        self.kind = kind  # "straight", "turn", "arc", "drive", "still"
        self.profile = profile
        self.sign = sign
        self.radius = radius_mm
        self.speed, self.turn_rate = speed, turn_rate
        self.linear = linear  # True if its speed is mm/s (can carry into the next move)
        if profile is not None:
            self.end = start_ms + profile.T * 1000
        elif kind == "drive":
            self.end = math.inf
        else:
            self.end = start_ms

    def local(self, ms):
        return (min(ms, self.end) - self.start) / 1000

    def speed_at(self, ms):
        if self.kind == "drive":
            return abs(self.speed)
        if self.profile is None:
            return 0.0
        return self.profile.at(self.local(ms))[1]

    def pose(self, ms):
        x, y, h = self.pose0
        t = self.local(ms)
        if self.kind == "straight":
            s = self.sign * self.profile.at(t)[0]
            return x + s * math.cos(math.radians(h)), y + s * math.sin(math.radians(h)), h
        if self.kind == "turn":
            # Pybricks: positive turn = clockwise = heading goes DOWN.
            return x, y, h - self.sign * self.profile.at(t)[0]
        if self.kind == "arc":
            s = self.sign * self.profile.at(t)[0]  # signed distance along the arc
            return _arc_pose(x, y, h, self.radius, s)
        if self.kind == "drive":
            if self.turn_rate == 0:
                s = self.speed * t
                return x + s * math.cos(math.radians(h)), y + s * math.sin(math.radians(h)), h
            radius = self.speed / math.radians(self.turn_rate)  # + = circle to the right
            if self.speed == 0:
                return x, y, h - self.turn_rate * t
            return _arc_pose(x, y, h, radius, self.speed * t)
        return x, y, h


def _arc_pose(x, y, h, radius, s):
    """Drive s mm along a circle of `radius` (Pybricks sign: + = to the right)."""
    hr = math.radians(h)
    side = 1 if radius > 0 else -1
    r = abs(radius)
    # Circle center is r mm to the robot's right (radius > 0) or left (< 0).
    cx = x + side * r * math.sin(hr)
    cy = y - side * r * math.cos(hr)
    dh = -side * s / r  # radians; right circle forward = clockwise
    dx, dy = x - cx, y - cy
    c, sn = math.cos(dh), math.sin(dh)
    return cx + c * dx - sn * dy, cy + sn * dx + c * dy, h + math.degrees(dh)


class FakeDriveBase:
    def __init__(self, start_pose_cm):
        x, y, h = start_pose_cm
        self.segments = [Segment(0, (x * 10, y * 10, h), "still")]
        self.straight_speed = 297
        self.straight_acc = (1113, 1113)
        self.turn_rate = 258
        self.turn_acc = (1159, 1159)
        self.carry_speed = 0.0  # mm/s carried in from a Stop.NONE move
        self.gyro = False
        self.dist0 = 0.0
        self.angle0 = h

    # -- helpers --
    @property
    def seg(self):
        return self.segments[-1]

    def pose_at(self, ms):
        for seg in reversed(self.segments):
            if seg.start <= ms:
                return seg.pose(ms)
        return self.segments[0].pose0

    def _begin(self, make, wait, then=None, label=""):
        now = clock.ms
        cur = self.seg
        moving_in = 0.0
        if cur.end > now and cur.linear:  # interrupting a move: keep its speed
            moving_in = cur.speed_at(now)
        elif self.carry_speed:
            moving_in = self.carry_speed
        if cur.end > now:
            cur.end = now
        new = make(now, cur.pose(now), moving_in)
        self.segments.append(new)
        none = then is not None and _stop_name(then) == "NONE"
        self.carry_speed = new.profile.vend if (none and new.profile and new.linear) else 0.0
        clock.note(label)
        if wait and new.end != math.inf:
            clock.advance_to(new.end)

    # -- Pybricks API --
    def settings(self, straight_speed=None, straight_acceleration=None,
                 turn_rate=None, turn_acceleration=None):
        if straight_speed is not None:
            self.straight_speed = min(abs(straight_speed), MAX_STRAIGHT_SPEED)
        if straight_acceleration is not None:
            a = straight_acceleration
            self.straight_acc = tuple(a) if isinstance(a, (tuple, list)) else (a, a)
        if turn_rate is not None:
            self.turn_rate = min(abs(turn_rate), MAX_TURN_RATE)
        if turn_acceleration is not None:
            a = turn_acceleration
            self.turn_acc = tuple(a) if isinstance(a, (tuple, list)) else (a, a)
        return (self.straight_speed, self.straight_acc, self.turn_rate, self.turn_acc)

    def use_gyro(self, use):
        self.gyro = use

    def straight(self, distance, then=None, wait=True):
        def make(now, pose, v0):
            p = Profile(distance, self.straight_speed, *self.straight_acc, v0=v0,
                        vend=self.straight_speed if then is not None and _stop_name(then) == "NONE" else 0)
            return Segment(now, pose, "straight", p, sign=1 if distance >= 0 else -1)
        self._begin(make, wait, then, fmt_call("straight", distance, **_kw(then, wait)))

    def turn(self, angle, then=None, wait=True):
        def make(now, pose, v0):
            p = Profile(angle, self.turn_rate, *self.turn_acc)
            return Segment(now, pose, "turn", p, sign=1 if angle >= 0 else -1, linear=False)
        self._begin(make, wait, then, fmt_call("turn", angle, **_kw(then, wait)))

    def arc(self, radius, angle=None, distance=None, then=None, wait=True):
        if (angle is None) == (distance is None):
            raise ValueError("arc() needs angle or distance, but not both")
        r = abs(radius)
        if angle is not None:
            s = r * math.radians(angle)
        else:
            s = distance

        def make(now, pose, v0):
            if r == 0:  # radius 0 is just a turn in place
                p = Profile(angle or 0, self.turn_rate, *self.turn_acc)
                return Segment(now, pose, "turn", p, sign=-1 if (angle or 0) * (radius or 1) < 0 else 1,
                               linear=False)
            # Pybricks limits the arc by both the straight speed and turn rate.
            vmax = min(self.straight_speed, math.radians(self.turn_rate) * r)
            none = then is not None and _stop_name(then) == "NONE"
            p = Profile(s, vmax, *self.straight_acc, v0=v0, vend=vmax if none else 0)
            return Segment(now, pose, "arc", p, sign=1 if s >= 0 else -1, radius_mm=radius)

        kw = {"angle": angle} if angle is not None else {"distance": distance}
        self._begin(make, wait, then, fmt_call("arc", radius, **kw, **_kw(then, wait)))

    def curve(self, radius, angle, then=None, wait=True):
        self.arc(radius, angle=angle, then=then, wait=wait)

    def drive(self, speed, turn_rate):
        def make(now, pose, v0):
            return Segment(now, pose, "drive", speed=speed, turn_rate=turn_rate)
        self._begin(make, False, None, fmt_call("drive", speed, turn_rate))

    def _halt(self, name):
        now = clock.ms
        if self.seg.end > now:
            self.seg.end = now
        self.carry_speed = 0.0
        self.segments.append(Segment(now, self.seg.pose(now), "still"))
        clock.note(f"{name}()")

    def stop(self):
        self._halt("stop")

    def brake(self):
        self._halt("brake")

    def hold(self):
        self._halt("hold")

    def done(self):
        return clock.ms >= self.seg.end

    def stalled(self):
        return False  # nothing to bump into in here

    def distance(self):
        return 0  # not tracked; add it if a mission ever needs it

    def angle(self):
        return -(self.pose_at(clock.ms)[2] - self.angle0)  # Pybricks: clockwise = positive

    def reset(self, distance=0, angle=0):
        pass

    def state(self):
        return (self.distance(), self.seg.speed_at(clock.ms), self.angle(), 0)


def _kw(then, wait):
    kw = {}
    if then is not None:
        kw["then"] = then
    if not wait:
        kw["wait"] = False
    return kw


# --- Fake motors, sensors, hub ---------------------------------------------

class FakeMotor:
    def __init__(self, name):
        self.name = name
        # (start ms, start angle, deg/s, end ms)
        self.moves = [(0.0, 0.0, 0.0, 0.0)]

    def angle_at(self, ms):
        for start, a0, rate, end in reversed(self.moves):
            if start <= ms:
                return a0 + rate * (min(ms, end) - start) / 1000
        return 0.0

    def _move(self, rate, duration_s, label, wait):
        now = clock.ms
        a = self.angle_at(now)
        start, a0, r, end = self.moves[-1]
        if end > now:
            self.moves[-1] = (start, a0, r, now)
        end = math.inf if duration_s is None else now + duration_s * 1000
        self.moves.append((now, a, rate, end))
        clock.note(f"{self.name}.{label}")
        if wait and end != math.inf:
            clock.advance_to(end)

    def run_angle(self, speed, rotation_angle, then=None, wait=True):
        speed = min(abs(speed), MOTOR_MAX_DEG_S)
        sign = 1 if rotation_angle * (1 if speed >= 0 else -1) >= 0 else -1
        self._move(sign * speed, abs(rotation_angle) / max(speed, 1e-6),
                   fmt_call("run_angle", speed, rotation_angle), wait)

    def run_target(self, speed, target_angle, then=None, wait=True):
        speed = min(abs(speed), MOTOR_MAX_DEG_S)
        delta = target_angle - self.angle_at(clock.ms)
        self._move(math.copysign(speed, delta), abs(delta) / max(speed, 1e-6),
                   fmt_call("run_target", speed, target_angle), wait)

    def run_time(self, speed, time, then=None, wait=True):
        self._move(max(-MOTOR_MAX_DEG_S, min(speed, MOTOR_MAX_DEG_S)), time / 1000,
                   fmt_call("run_time", speed, time), wait)

    def run_until_stalled(self, speed, then=None, duty_limit=None):
        # Nothing to stall against in the simulator: pretend it hits
        # something after half a second.
        self._move(max(-MOTOR_MAX_DEG_S, min(speed, MOTOR_MAX_DEG_S)), 0.5,
                   fmt_call("run_until_stalled", speed), True)
        return self.angle_at(clock.ms)

    def run(self, speed):
        self._move(speed, None, fmt_call("run", speed), False)

    def dc(self, duty):
        if duty == 0:
            self._move(0, 0, "dc(0)", False)
        else:
            self._move(duty / 100 * MOTOR_MAX_DEG_S, None, fmt_call("dc", duty), False)

    def stop(self):
        self._move(0, 0, "stop()", False)

    def brake(self):
        self._move(0, 0, "brake()", False)

    def hold(self):
        self._move(0, 0, "hold()", False)

    def done(self):
        return clock.ms >= self.moves[-1][3]

    def stalled(self):
        return False

    def angle(self):
        return int(self.angle_at(clock.ms))

    def reset_angle(self, angle=0):
        now = clock.ms
        self.moves.append((now, angle, 0.0, now))

    def speed(self):
        return 0


class FakeColorSensor:
    def color(self, surface=True):
        from pybricks.parameters import Color
        return Color.WHITE

    def reflection(self):
        return 50

    def ambient(self):
        return 10

    def hsv(self, surface=True):
        return (0, 0, 100)

    def lights(self):
        return types.SimpleNamespace(on=lambda *a: None, off=lambda: None)


class _Anything:
    """Swallows any call: hub.display.number(5), hub.light.on(...), etc."""

    def __getattr__(self, name):
        return lambda *a, **k: None


class FakeHub:
    def __init__(self, drive_base):
        self._db = drive_base
        self.display = _Anything()
        self.light = _Anything()
        self.system = _Anything()
        self.speaker = types.SimpleNamespace(
            beep=lambda frequency=500, duration=100: (clock.note("beep!"), clock.advance_to(clock.ms + duration)),
            volume=lambda *a: None, play_notes=lambda *a, **k: None)
        self.buttons = types.SimpleNamespace(pressed=lambda: set())
        self.battery = types.SimpleNamespace(voltage=lambda: 8000, current=lambda: 100)
        self.imu = types.SimpleNamespace(
            heading=lambda: -(self._db.pose_at(clock.ms)[2] - self._db.angle0),
            tilt=lambda: (0, 0), reset_heading=lambda *a: None, ready=lambda: True,
            stationary=lambda: True)


# --- Fake pybricks.tools (installed before the mission is imported) ---------

class StopWatch:
    def __init__(self):
        self._start = clock.ms

    def time(self):
        return int(clock.ms - self._start)

    def reset(self):
        self._start = clock.ms

    def pause(self):
        pass

    def resume(self):
        pass


def _wait(ms):
    clock.advance_to(clock.ms + ms)


def install_fake_tools():
    sys.path.insert(0, REPO)
    # The real pybricks package is just do-nothing stubs on a laptop. Keep it,
    # but swap in our own wait()/StopWatch so they use the simulated clock.
    import pybricks.tools as tools

    def no_async(*a, **k):
        raise NotImplementedError("the simulator only does plain sync missions")

    tools.wait = _wait
    tools.StopWatch = StopWatch
    tools.multitask = tools.run_task = no_async


# --- Run a mission ----------------------------------------------------------

def run_mission(number, start_pose):
    install_fake_tools()
    import importlib
    import rosie_rover
    mission = importlib.import_module(f"m{number}")

    drive_base = FakeDriveBase(start_pose)
    left, right = FakeMotor("left_top_motor"), FakeMotor("right_top_motor")
    hub = FakeHub(drive_base)
    rosie_rover.reset_drive_settings(drive_base)  # same as rosie_rover_main.py
    clock.log.clear()

    error = None
    try:
        mission.run(left, right, FakeColorSensor(), FakeColorSensor(), hub, drive_base)
    except SimTimeout as e:
        error = str(e)
    finished = clock.ms
    # Anything still going (drive(), dc(), wait=False) gets cut off when the
    # mission returns, like rosie_rover_main.py's next loop would.
    end = max(finished, *(s.end for s in drive_base.segments if s.end != math.inf))
    for seg in drive_base.segments:
        if seg.end == math.inf:
            seg.end = finished
    return drive_base, left, right, finished, end, error


# --- Drawing ----------------------------------------------------------------

def load_font(size):
    for path in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


class Painter:
    def __init__(self, width_px):
        field = Image.open(os.path.join(HERE, "field.jpg")).convert("RGB")
        self.scale = width_px / field.width
        self.field = field.resize((width_px, round(field.height * self.scale)), Image.LANCZOS)
        self.px_x = (FIELD_IMG_RIGHT - FIELD_IMG_LEFT) / FIELD_W_CM * self.scale
        self.px_y = (FIELD_IMG_BOTTOM - FIELD_IMG_TOP) / FIELD_H_CM * self.scale
        robot = Image.open(os.path.join(HERE, "robot.png")).convert("RGBA")
        self.robot = robot.resize((max(1, round(ROBOT_W_CM * self.px_x)), max(1, round(ROBOT_L_CM * self.px_y))),
                                  Image.LANCZOS)
        self.font = load_font(max(12, width_px // 60))
        self.big_font = load_font(max(20, width_px // 25))

    def to_px(self, x_mm, y_mm):
        return (FIELD_IMG_LEFT * self.scale + x_mm / 10 * self.px_x,
                FIELD_IMG_BOTTOM * self.scale - y_mm / 10 * self.px_y)

    def robot_corners_cm(self, x_mm, y_mm, h):
        hr = math.radians(h)
        fx, fy = math.cos(hr), math.sin(hr)
        lx, ly = -fy, fx
        x, y = x_mm / 10, y_mm / 10
        front = ROBOT_L_CM - AXLE_FROM_BACK_CM
        back = -AXLE_FROM_BACK_CM
        w = ROBOT_W_CM / 2
        return [(x + a * fx + b * lx, y + a * fy + b * ly)
                for a, b in ((front, w), (front, -w), (back, -w), (back, w))]

    def frame(self, number, t_ms, pose, trail, arm_deg, command, done):
        img = self.field.copy()
        d = ImageDraw.Draw(img)
        if len(trail) > 1:
            d.line([self.to_px(x, y) for x, y in trail], fill=(255, 140, 0), width=max(3, img.width // 300))

        x, y, h = pose
        # Rotate the sprite about the axle point, then paste it there.
        # The sprite faces north (up), so turn it by (heading - 90).
        sprite = self.robot
        axle_from_top = (ROBOT_L_CM - AXLE_FROM_BACK_CM) / ROBOT_L_CM * sprite.height
        pad = Image.new("RGBA", (sprite.width, round(2 * max(axle_from_top, sprite.height - axle_from_top))))
        pad.paste(sprite, (0, round(pad.height / 2 - axle_from_top)))
        rot = pad.rotate(h - 90, resample=Image.BICUBIC, expand=True)
        px, py = self.to_px(x, y)
        img.paste(rot, (round(px - rot.width / 2), round(py - rot.height / 2)), rot)

        # 1 cm of slack so a robot parked flush against a wall doesn't count.
        bonk = any(not (-1 <= cx <= FIELD_W_CM + 1 and -1 <= cy <= FIELD_H_CM + 1)
                   for cx, cy in self.robot_corners_cm(x, y, h))
        if bonk:
            d.text((px, py - 40 * self.scale * 2), "BONK!", fill=(220, 0, 0), font=self.big_font,
                   anchor="mb", stroke_width=3, stroke_fill="white")

        lines = [f"Mission {number:02}   {t_ms / 1000:4.1f} s",
                 f"x {x / 10:5.1f} cm   y {y / 10:5.1f} cm   heading {h % 360:5.1f}\u00b0",
                 f"arm {arm_deg:5.0f}\u00b0",
                 command or ""]
        if done:
            lines[-1] = "Finished!"
        box_w = max(d.textlength(s, font=self.font) for s in lines) + 20
        line_h = self.font.size * 1.35
        top = 0.30 * img.height
        left = 0.36 * img.width
        d.rounded_rectangle((left, top, left + box_w, top + line_h * len(lines) + 12), 8,
                            fill=(255, 255, 255), outline=(60, 60, 60), width=2)
        for i, s in enumerate(lines):
            d.text((left + 10, top + 6 + i * line_h), s, fill=(20, 20, 20), font=self.font)
        return img


def render(number, start_pose, width_px, fps, speed):
    drive_base, left, right, finished, end, error = run_mission(number, start_pose)
    print(f"Finished Mission {number:02}, time {finished / 1000:.1f} seconds (simulated)")
    if error:
        print("Simulator stopped early:", error)

    painter = Painter(width_px)
    step_ms = 1000 / fps * speed
    hold_ms = 1200  # linger on the last frame a bit
    frames, trail = [], []
    t = 0.0
    while True:
        tt = min(t, end)
        pose = drive_base.pose_at(tt)
        trail.append(pose[:2])
        command = ""
        for when, text in clock.log:
            if when <= tt:
                command = text
        arm = (left.angle_at(tt) + right.angle_at(tt)) / 2
        frames.append(painter.frame(number, tt, pose, trail, arm, command, tt >= end))
        if t >= end + hold_ms:
            break
        t += step_ms
    return frames


def show_window(frames, fps, title):
    import tkinter as tk
    from PIL import ImageTk

    root = tk.Tk()
    root.title(title)
    photos = [ImageTk.PhotoImage(f) for f in frames]
    label = tk.Label(root, image=photos[0])
    label.pack()
    tk.Label(root, text="space = replay    q = quit").pack()
    state = {"i": 0, "job": None}

    def tick():
        label.configure(image=photos[state["i"]])
        state["i"] += 1
        if state["i"] < len(photos):
            state["job"] = root.after(int(1000 / fps), tick)

    def replay(_=None):
        if state["job"]:
            root.after_cancel(state["job"])
        state["i"] = 0
        tick()

    root.bind("<space>", replay)
    root.bind("q", lambda e: root.destroy())
    root.bind("<Escape>", lambda e: root.destroy())
    root.lift()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    tick()
    root.mainloop()


def main():
    ap = argparse.ArgumentParser(description="Watch a Rosie Rover mission drive on the field.")
    ap.add_argument("mission", type=int, help="mission number, e.g. 17 runs m17.py")
    ap.add_argument("--start", nargs=3, type=float, metavar=("X", "Y", "HEADING"),
                    help="start pose: cm from left wall, cm from south wall, heading (90 = north)")
    ap.add_argument("--gif", metavar="FILE", help="also save an animated GIF")
    ap.add_argument("--no-window", action="store_true", help="don't open the animation window")
    ap.add_argument("--speed", type=float, default=1.0, help="playback speed (2 = twice as fast)")
    ap.add_argument("--width", type=int, default=1100, help="window width in pixels")
    args = ap.parse_args()

    if args.start:
        start = tuple(args.start)
    elif args.mission in START_POSES:
        start = START_POSES[args.mission]
    else:
        start = DEFAULT_START
        print(f"No start position saved for m{args.mission} yet -- guessing {start}. "
              "Use --start X Y HEADING, or add it to START_POSES.")

    fps = 30
    frames = render(args.mission, start, args.width, fps, args.speed)

    if args.gif:
        small = [f.resize((f.width * 2 // 3, f.height * 2 // 3), Image.LANCZOS).convert(
            "P", palette=Image.ADAPTIVE, colors=128) for f in frames[::2]]
        small[0].save(args.gif, save_all=True, append_images=small[1:],
                      duration=int(2000 / fps), loop=0, optimize=True)
        print(f"Saved {args.gif}")
    if not args.no_window:
        show_window(frames, fps, f"Rosie Rover simulator - m{args.mission}")


if __name__ == "__main__":
    main()
