from __future__ import annotations

import asyncio
import math
import ALPHANUMERIC
from dataclasses import dataclass
from typing import Iterable, Tuple, List

# import RPIO as GPIO
import RPi.GPIO as GPIO

from MotorShield import PiMotor as pimotor

GPIO.setmode(GPIO.BOARD)

# setup LED pins
leftLED_pin = 13  # pin33
rightLED_pin = 19  # pin35
upLED_pin = 16  # pin 36
downLED_pin = 26  # pin37
GPIO.setup(leftLED_pin, GPIO.OUT)
GPIO.setup(rightLED_pin, GPIO.OUT)
GPIO.setup(upLED_pin, GPIO.OUT)
GPIO.setup(downLED_pin, GPIO.OUT)
# setup button pins
limit_switch = 18
left_btn = 4
right_btn = 17
GPIO.setup(limit_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(left_btn, GPIO.IN)
GPIO.setup(right_btn, GPIO.IN)


# Bounds for radius, in mm
RADIUS_MIN = 0.0
RADIUS_MAX = 10.0

# Steps required to traverse bounds
STEPS_FOR_FULL_ROTATION = int(64 * 30 * 3)
STEPS_FOR_FULL_EXTENSION = 500  # TODO: FIX

# Deltas computed based on above values
STEP_DELTA_RADIUS = (RADIUS_MAX - RADIUS_MIN) / STEPS_FOR_FULL_EXTENSION
STEP_DELTA_ROTATION = 2 * math.pi / STEPS_FOR_FULL_ROTATION

# How long to sleep twixt steps
STEP_TIME = 0.01


# Represents a cartesian coordinate
@dataclass
class Cartesian:
    x: float
    y: float

    @property
    def mag(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def polar(self) -> Polar:
        r = self.mag
        t = math.atan2(self.y, self.x)
        return Polar(r, t)

    def __add__(self, other: Cartesian) -> Cartesian:
        return Cartesian(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Cartesian) -> Cartesian:
        return Cartesian(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> Cartesian:
        return Cartesian(self.x * other, self.y * other)

    def segment(self, max_length: float) -> List[Cartesian]:
        # Breaks this cartesian coordinate into a list of smaller coordinates representing the steps betwixt
        length = self.mag
        min_req = math.ceil(length / max_length)
        seg = self * (1/min_req)
        results = []
        for i in range(min_req):
            results.append(seg * (i+1))
        return results


# Represents a polar coordinate
@dataclass
class Polar:
    r: float
    theta: float

    @property
    def canonical(self) -> Polar:
        r = self.r
        t = self.theta

        # Fix negative
        if r < 0:
            r = -r
            t = t + math.pi

        # Fix t to be in pi thru -pi
        cull_count = math.trunc(t / math.pi)
        t = t - (cull_count * math.pi * 2)
        return Polar(r, t)

    @property
    def cartesian(self) -> Cartesian:
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)
        return Cartesian(x, y)

    # Imaginary multiplication
    def cmul(self, other: Polar) -> Polar:
        return Polar(self.r * other.r, self.theta + other.theta).canonical


# Class to plan out motions
class Plan:
    position_polar: Polar
    position_ticks: Tuple[int, int]

    program: List[Tuple[int, int]] = []

    def __init__(self, initial_pos: Polar, initial_ticks: Tuple[int, int]):
        self.position_polar = initial_pos
        self.position_ticks = initial_ticks

    def goto_polar(self, target_coord: Polar):
        # Find the change in angle/radius we need to make
        delta_angle = target_coord.theta - self.position_polar.theta
        delta_radius = target_coord.r - self.position_polar.r

        # Convert to changes in ticks
        delta_spinnner_tick = int(delta_angle / STEP_DELTA_ROTATION)
        delta_slide_tick = int(delta_radius / STEP_DELTA_RADIUS)

        # Find new target ticks
        self.position_ticks = (self.position_ticks[0] + delta_spinnner_tick,
                               self.position_ticks[1] + delta_slide_tick)

        # Store to plan
        self.program.append(self.position_ticks)

        # Update our polar as well
        self.position_polar = target_coord

    def __iter__(self) -> Iterable[Tuple[int, int]]:
        yield from self.program


DEFAULT_START_POS = Cartesian(RADIUS_MIN, 0).polar

# Encoder sequence
SEQ = [0b00, 0b01, 0b11, 0b10]

# Encoder pins (fmt A, B)
# Pins are, physically, 24:23 and 8:25
# Translates to 18:16 and 24:22
# ENCODER_1_PINS = (18, 16)
# ENCODER_2_PINS = (24, 22)

# limit switch: P18 -> 12
LIMIT_SWITCH_PIN = 12


BOUND = 2147483647
def read_locations() -> Tuple[int, int]:
    with open("/sys/enc/dot", 'r') as f:
        text = f.read()
        one, two = text.split(' ')
        one, two = int(one), int(two)
        if one > BOUND:
            one -= (2*BOUND)
        if two > BOUND:
            two -= (2*BOUND)
        return one, two


class EncoderTracker:
    # Store the targets
    motor1_dest: int
    motor2_dest: int

    motor1: pimotor.Motor
    motor2: pimotor.Motor

    def __init__(self, motor1: pimotor.Motor, motor2: pimotor.Motor):
        # Store the motors
        self.motor1 = motor1
        self.motor2 = motor2

    async def goto_destinations(self, motor1_dest: int, motor2_dest: int, spin_speed: int, slide_speed: int):
        assert 0 < spin_speed <= 100
        assert 0 < slide_speed <= 100

        # Get the current positions
        done1, done2 = False, False
        tolerance = 64

        # Iterate until within tolerance
        while not (done1 and done2):
            # Get current offsets
            positions = read_locations()
            d1 = motor1_dest - positions[0]
            d2 = motor2_dest - positions[1]

            # Check m1
            if done1:
                # If we're already done, do nothing
                pass
            elif d1 > tolerance:
                self.motor1.forward(spin_speed)
                GPIO.output(leftLED_pin, True)
                GPIO.output(rightLED_pin, False)
            elif d1 < -tolerance:
                self.motor1.reverse(spin_speed)
                GPIO.output(leftLED_pin, False)
                GPIO.output(rightLED_pin, True)
            else:
                done1 = True
                self.motor1.stop()
                GPIO.output(leftLED_pin, False)
                GPIO.output(rightLED_pin, False)

            # Check m2
            if done2:
                # If we're already done, do nothing
                pass
            elif d2 > tolerance:
                self.motor2.forward(slide_speed)
                GPIO.output(upLED_pin, True)
                GPIO.output(downLED_pin, False)
            elif d2 < -tolerance:
                self.motor2.reverse(slide_speed)
                GPIO.output(upLED_pin, False)
                GPIO.output(downLED_pin, True)
            else:
                done2 = True
                self.motor2.stop()
                GPIO.output(upLED_pin, False)
                GPIO.output(downLED_pin, False)

            # Sleep for a bit
            await asyncio.sleep(STEP_TIME)

    async def execute(self, p: Plan, spin_speed: int, slide_speed: int) -> None:
        for step in p:
            await self.goto_destinations(step[0], step[1], spin_speed, slide_speed)


# Create motorstates using the gpio
spinner_motor = pimotor.Motor("MOTOR1", 1)
slider_motor = pimotor.Motor("MOTOR2", 1)


# The main runtime
def main():
    # Make our corresponding encoders
    spinner_encoder = EncoderTracker(spinner_motor, slider_motor)

    # Get our asyncio event loop
    loop = asyncio.get_event_loop()

    # Have the motor go for a little bit
    SPIN_SPEED = 27
    SLIDE_SPEED = 40
    reset_motion = spinner_encoder.goto_destinations(0, 0, SPIN_SPEED)

    # Run it
    print("Attempting run")
    loop.run_until_complete(reset_motion)

    # Spin backwards till we hit root
    slider_motor.reverse(50)
    while GPIO.input(limit_switch):
        pass
    slider_motor.stop()

    # Save this as the base of the slider
    slider_base = read_locations()[1]

    # Assume its already zeroed
    spinner_base = read_locations()[0]
    tick_base = (spinner_base, slider_base)

    # Make as a plan
    plan = Plan(DEFAULT_START_POS, tick_base)

    # Now we make what we want to draw
    # Create all of the points
    a = ALPHANUMERIC.get_letter('a')
    points = a.waypoints

    # Convert to polar
    pol_points = [Polar(p[1]*0.1, 5+p[0]) for p in points]

    # Add to the plan
    for pol in pol_points:
        plan.goto_polar(pol)

    # Go for it
    plan_execution = spinner_encoder.execute(plan, SPIN_SPEED, SLIDE_SPEED)
    loop.run_until_complete(plan_execution)


if __name__ == '__main__':
    err = None
    try:
        main()
    except Exception as e:
        err = e
        pass
    finally:
        try:
            spinner_motor.stop()
            slider_motor.stop()
        except RuntimeError:
            pass
        raise err
