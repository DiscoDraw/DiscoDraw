from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import Iterable, Tuple, List

# import RPIO as GPIO
import RPi.GPIO as GPIO

from MotorShield import PiMotor as pimotor

GPIO.setmode(GPIO.BOARD)

# Bounds for radius, in mm
RADIUS_MIN = 5.0
RADIUS_MAX = 500.0

# Steps required to traverse bounds
STEPS_FOR_FULL_ROTATION = int(64 * 30 * 3)
STEPS_FOR_FULL_EXTENSION = int(64 * 10)  # TODO: FIX

# Deltas computed based on above values
STEP_DELTA_RADIUS = (RADIUS_MAX - RADIUS_MIN) / STEPS_FOR_FULL_EXTENSION
STEP_DELTA_ROTATION = 2 * math.pi / STEPS_FOR_FULL_ROTATION

# How long to sleep twixt steps
STEP_TIME = 0.001


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


# Encodes a single time-step's actions, for a single motor
@dataclass
class MotorStep:
    delta_step: int

    @property
    def delta_radius(self):
        return self.delta_step * STEP_DELTA_RADIUS

    @property
    def delta_rotation(self):
        return self.delta_step * self.delta_rotation


# Make standard steps
MotorStep.NEUTRAL = MotorStep(0)
MotorStep.FORWARD = MotorStep(1)
MotorStep.BACKWARD = MotorStep(-1)


# Encodes the sum-total of actions a machine can make in a single step
@dataclass
class MachineStep:
    slider_step: MotorStep
    spinner_step: MotorStep

    def is_neutral(self):
        return self.slider_step.delta_step == 0 and self.spinner_step.delta_step == 0


# Yields the neighbors of a point (IE all points within 1 step). Includes the neutral step (IE no movement)
def neighbors(p: Polar) -> Iterable[Tuple[Polar, MachineStep]]:
    step_options = (MotorStep.BACKWARD, MotorStep.NEUTRAL, MotorStep.FORWARD)
    for slider_step in step_options:
        for spinner_step in step_options:
            new_coord = Polar(p.r + slider_step.delta_radius, p.theta + spinner_step.delta_rotation)
            step_required = MachineStep(slider_step, spinner_step)
            yield new_coord, step_required


# Class to plan out motions
class Plan:
    position: Polar
    program: List[MachineStep] = []

    def __init__(self, initial_pos: Polar):
        self.position = initial_pos

    def goto_polar(self, target_coord: Polar):
        # Make a cartesian version of the target
        target_coord_cart = target_coord.cartesian

        # Create an evaluation function for proximity to target coord
        def score(candidate_move: Tuple[Polar, MachineStep]) -> float:
            # First make the candidate cartesian
            candidate_pos = candidate_move[0].cartesian

            # Find the distance twixt them
            diff = target_coord_cart - candidate_pos
            diff_mag = diff.mag

            return diff_mag

        # Go until we get a neutral step
        done = False
        while not done:
            # Get the step that will bring us closest
            next_step = min(neighbors(self.position), key=score)

            # Check if we should stop
            if next_step[1].is_neutral():
                done = True
            else:
                # Update state, and add to plan
                self.position = next_step[0]
                self.program.append(next_step[1])

    def __iter__(self) -> Iterable[MachineStep]:
        yield from self.program


# Class to track machine state and execute motions
class MachineState:
    spinner_state: EncoderTracker
    slider_state: EncoderTracker

    def __init__(self, spinner: EncoderTracker, slider: EncoderTracker):
        self.spinner_state = spinner
        self.slider_state = slider

    def execute(self, plan: Plan):
        # Execute each machine step in sequence
        for step in plan:
            # Apply the steps
            # self.spinner_state.apply(step.spinner_step)
            # self.slider_state.apply(step.slider_step)
            pass


DEFAULT_START_POS = Cartesian(RADIUS_MIN, 0).polar

# Encoder sequence
SEQ = [0b00, 0b01, 0b11, 0b10]

# Encoder pins (fmt A, B)
# Pins are, physically, 24:23 and 8:25
# Translates to 18:16 and 24:22
ENCODER_1_PINS = (18, 16)
ENCODER_2_PINS = (24, 22)

# limit switch: P18 -> 12
LIMIT_SWITCH_PIN = 12


class EncoderTracker:
    def __init__(self, motor: pimotor.Motor, pin_a: int, pin_b: int):
        # Store the motor
        self.motor = motor

        # Store the pins
        self.pin_a = pin_a
        self.pin_b = pin_b

        # Add a callback for when they change
        # GPIO.add_interrupt_callback(self.pin_a, self.callback,
        #                             pull_up_down=GPIO.PUD_UP, threaded_callback=True)
        # GPIO.add_interrupt_callback(self.pin_b, self.callback,
        #                             pull_up_down=GPIO.PUD_UP, threaded_callback=True)
        for pin in self.pin_a, self.pin_b:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH)
            GPIO.add_event_callback(pin, self.callback)

        # Store the initial state
        # pin_state = (GPIO.input(pin_a), GPIO.input(pin_b))

        # Store the number of steps remaining
        self.steps_remaining = 0
        self.idle = True

        # Store the last pin state
        self.last_seq = self.get_seq()

    # Get the current state of our pins
    def get_seq(self) -> int:
        a, b = GPIO.input(self.pin_a), GPIO.input(self.pin_b)
        return (a ^ b) | b << 1

    # Called whenever the encoder changes states.
    # For now we assume this is a change in the direction we expect
    # For later we will allow handling unexpected motion
    def callback(self, channel):
        # Get the current seq
        curr_seq = self.get_seq()

        # See how far it has changed
        delta = (curr_seq - self.last_seq) % 4

        # Update our values
        self.last_seq = curr_seq
        self.steps_remaining -= delta

        # Stop. May overshoot by a certain amount
        if self.steps_remaining <= 0:
            self.motor.stop()
            self.steps_remaining = 0
            self.idle = True

    async def move_steps(self, num_steps: int, speed: int):
        assert 0 < speed <= 100

        # Get the absolute number of steps remaining
        self.steps_remaining = abs(num_steps)

        # Start the motor spinning
        if num_steps > 0:
            self.motor.forward(speed)
            self.idle = False
        elif num_steps < 0:
            self.motor.reverse(speed)
            self.idle = False

        # Wait till the motion is done
        while True:
            await asyncio.sleep(0.1)
            if self.idle:
                break


# Force an exception
def failfast():
    raise Exception("Abort")


# Create motorstates using the gpio
spinner_motor = pimotor.Motor("MOTOR1", 1)
slider_motor = pimotor.Motor("MOTOR2", 1)


# The main runtime
def main():
    # Make our corresponding encoders
    spinner_encoder = EncoderTracker(spinner_motor, *ENCODER_1_PINS)
    slider_encoder = EncoderTracker(slider_motor, *ENCODER_2_PINS)

    # Get our asyncio event loop
    loop = asyncio.get_event_loop()

    # Have the motor go for a little bit
    SPEED = 26
    motion = spinner_encoder.move_steps(STEPS_FOR_FULL_ROTATION, SPEED)

    # Run it
    print("Attempting run")
    loop.run_until_complete(motion)

    failfast()

    # Spin backwards till we hit root
    # while not "LIMIT_SWITCH":
    # pass

    # Make the machine.
    # machine = MachineState(spinner, slider)

    # Make the plan. We assume the arm is pointed east, IE in the positive x axis direction, denoting zero rotation
    plan = Plan(DEFAULT_START_POS)

    # Extend 1 foot, approx
    extended = Cartesian(RADIUS_MAX / 2, 0).polar
    plan.goto_polar(extended)

    # Draw a hexagon
    pos = extended
    delta = Polar(1, math.pi / 3)
    for i in range(6):
        pos = pos.cmul(delta)
        plan.goto_polar(pos)

    # Go for it, dude
    # machine.execute(plan)

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
