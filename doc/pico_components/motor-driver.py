
import time
from machine import Pin, I2C
from picobricks import MotorDriver

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
motor = MotorDriver(i2c)

motor.servo(1,90)
motor.servo(2,90)
motor.servo(3,90)
motor.servo(4,90)

# motor.dc(which, speed, direction)
