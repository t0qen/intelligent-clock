from machine import Pin, I2C, PWM
from picobricks import SSD1306_I2C, WS2812, MotorDriver

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# clear oled
oled.fill(0)
oled.show()

# clear rgb let
ws2812 = WS2812(6, brightness=1)
ws2812.pixels_fill((0, 0, 0))
ws2812.pixels_show()

# clear motor & servos
motor = MotorDriver(i2c)
for i in range(2):
    motor.dc(i + 1, 0, 0)
for i in range(4):
    motor.servo(i + 1, 0)

# clear leds
led = Pin(7, Pin.OUT)
led.low()
led = Pin(8, Pin.OUT)
led.low()

# clear relay
relay = Pin(12, Pin.OUT)
relay.low()

# clear buzzer
buzzer = PWM(Pin(20))
buzzer.duty_u16(0)



print('Cleared')