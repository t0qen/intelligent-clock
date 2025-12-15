import time
from machine import Pin, I2C
from picobricks import MotorDriver

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
motor = MotorDriver(i2c)

"""
Notes
=====

servo 1 : right leg
servo 3 : left leg
servo 2 : base
"""

def reset_base():
    motor.servo(2, 100)


def move_legs(angle):
    motor.servo(3, angle)
    motor.servo(1, 180-angle)

def setup_pas():
    move_legs(140)
    motor.servo(2, 150)

def pas():
    motor.servo(2, 100)
    move_legs(120)
    time.sleep(0.2)
    motor.servo(2, 60)
    move_legs(40)
    time.sleep(0.5)
    #motor.servo(2, 100)

def test():
    move_legs(110)
    time.sleep(0.1)
    motor.servo(2, 130)

def reset():
    move_legs(40)
    motor.servo(2, 70)
motor.servo(2, 70)
move_legs(40)

for i in range(10):
    reset()
    time.sleep(0.7)
    test()
    time.sleep(0.7)