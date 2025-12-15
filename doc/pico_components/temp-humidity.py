from machine import Pin, I2C
from picobricks import SHTC3
i2c = I2C(0, scl=Pin(5), sda=Pin(4))

shtc_sensor = SHTC3(i2c)

while True:
    tempSHTC = shtc_sensor.temperature()
    humiditySHTC = shtc_sensor.humidity()
    print("Temp : ", tempSHTC)
    print("Humidity : ", humiditySHTC)