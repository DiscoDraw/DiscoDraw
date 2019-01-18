from __future__ import annotations
import math
import time
from dataclasses import dataclass

class GPIO:
    HIGH = 0
    LOW = 0
    OUT = 0
    @classmethod
    def setup(cls, pin, mode):
        pass
    @classmethod
    def output(cls, pin, val):
        pass


# Assume all floats are in mm/radians
from typing import Iterable, Tuple, List

# Bounds for radius, in mm
RADIUS_MIN = 5
RADIUS_MAX = 500

# Steps required to traverse bounds
STEPS_FOR_FULL_ROTATION = 1000
STEPS_FOR_FULL_EXTENSION = 500

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


# Raw GPIO interface to the motors
class StepperState:
    # Codes for motor
    SEQ = [[1, 0, 1, 0],
           [0, 1, 1, 0],
           [0, 1, 0, 1],
           [1, 0, 0, 1]]

    def __init__(self, pin_config):
        # Initialize our index and config
        self.index = 0
        self.config = pin_config

        # Initialize the motor
        GPIO.setup(self.config["en1"], GPIO.OUT)
        GPIO.setup(self.config["en2"], GPIO.OUT)
        GPIO.setup(self.config["c1"], GPIO.OUT)
        GPIO.setup(self.config["c2"], GPIO.OUT)
        GPIO.setup(self.config["c3"], GPIO.OUT)
        GPIO.setup(self.config["c4"], GPIO.OUT)

        # Set the pins to their default state
        GPIO.output(self.config["en1"], GPIO.HIGH)
        GPIO.output(self.config["en2"], GPIO.HIGH)
        self.output(StepperState.SEQ[self.index])

    def output(self, code):
        GPIO.output(self.config["c1"], code[0])
        GPIO.output(self.config["c2"], code[1])
        GPIO.output(self.config["c3"], code[2])
        GPIO.output(self.config["c4"], code[3])

    def step_forward(self):
        self.index += 1
        if self.index >= len(StepperState.SEQ):
            self.index = 0
        self.output(StepperState.SEQ[self.index])

    def step_backward(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(StepperState.SEQ) - 1
        self.output(StepperState.SEQ[self.index])

    def apply(self, step: MotorStep):
        if step == MotorStep.NEUTRAL:
            return
        elif step == MotorStep.FORWARD:
            self.step_forward()
        elif step == MotorStep.BACKWARD:
            self.step_backward()


# Yields the neighbors of a point (IE all points within 1 step). Includes the neutral step (IE no movement)
def neighbors(p: Polar) -> Iterable[Tuple[Polar, MachineStep]]:
    step_options = (MotorStep.BACKWARD, MotorStep.NEUTRAL, MotorStep.FORWARD)
    for slider_step in step_options:
        for spinner_step in step_options:
            new_coord = Polar(p.r + slider_step.delta_radius, p.theta + spinner_step.delta_rotation)
            step_required = MachineStep(slider_step, spinner_step)
            yield new_coord, step_required


# Waits for steppers to finish a movement
def tick():
    time.sleep(STEP_TIME)


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
    spinner_state: StepperState
    slider_state: StepperState

    def __init__(self, spinner: StepperState, slider: StepperState):
        self.spinner_state = spinner
        self.slider_state = slider

    def execute(self, plan: Plan):
        # Execute each machine step in sequence
        for step in plan:
            # Apply the steps
            self.spinner_state.apply(step.spinner_step)
            self.slider_state.apply(step.slider_step)

            # Delay
            tick()


STEPPER1_PINS = {"en1": 11, "en2": 22, "c1": 13, "c2": 15, "c3": 18, "c4": 16}
STEPPER2_PINS = {"en1": 19, "en2": 32, "c1": 21, "c2": 23, "c3": 24, "c4": 26}
DEFAULT_START_POS = Cartesian(RADIUS_MIN, 0).polar


# The main runtime
def main():
    # Create motorstates using the gpio
    spinner = StepperState(STEPPER1_PINS)
    slider = StepperState(STEPPER2_PINS)

    # Spin backwards till we hit root
    while not "LIMIT_SWITCH":
        slider.step_forward()
        tick()

    # Make the machine.
    machine = MachineState(spinner, slider)

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
    machine.execute(plan)


if __name__ == '__main__':
    main()