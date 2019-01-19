#!/user/bin/python
from MotorShield import PiMotor
import time

m1 = PiMotor.Stepper("STEPPER1")

# Rotate Stepper 1 Contiously in forward/backward direction

delay = .01

for x in range(10):
    delay = delay + .01
    print("delay: ", delay)
    m1.forward(delay, 10)  # Delay and rotations
    m1.disable()
    time.sleep(4)
# for i in range(5):
# m1.forward(0.1,10)  # Delay and rotations
# time.sleep(2)
# m1.backward(0.1,10)
# time.sleep(2)
