#!/user/bin/python
from MotorShield import PiMotor
import time

m1 = PiMotor.Stepper("STEPPER1")

# Rotate Stepper 1 Contiously in forward/backward direction
m1.forward(0.1,10)  # Delay and rotations
m1.disable()
# for i in range(5):
    # m1.forward(0.1,10)  # Delay and rotations
    # time.sleep(2)
    # m1.backward(0.1,10)
    # time.sleep(2)
