#!/user/bin/python
from MotorShield import PiMotor
import time

m1 = PiMotor.Stepper("STEPPER1")

# Rotate Stepper 1 Contiously in forward/backward direction
test=1
delay = .05

if(test==1):
    for x in range(20):
        delay = delay + .005
        delay=float('%.3f'%(delay))
        print("delay: ", delay)
        m1.forward(delay, 20)  # Delay and rotations
        #m1.disable()
        time.sleep(1)
if(test==2):
    m1.forward(delay,30)
# for i in range(5):
# m1.forward(0.1,10)  # Delay and rotations
# time.sleep(2)
# m1.backward(0.1,10)
# time.sleep(2)
