from machine import Pin, ADC

light_level = ADC(27)

while True:
    print(int(light_level.read_u16() / 1000))