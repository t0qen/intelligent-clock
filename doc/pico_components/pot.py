from machine import Pin, ADC

pot = ADC(26)

while True:
    print(int(pot.read_u16() / 1000))