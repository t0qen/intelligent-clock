from machine import Pin, I2C
from picobricks import NEC_16

ir_data_formated = ""
data_received = False

IR_CODES = {
    69: "BTN_1",
    70: "BTN_2",
    71: "BTN_3",
    68:"BTN_4",
    64: "BTN_5",
    67: "BTN_6",
    7: "BTN_7",
    21: "BTN_8",
    9: "BTN_9",
    25: "BTN_0",
    22: "STAR",
    13: "ASH",
    28: "OK",
    24: "UP",
    82: "DOWN",
    8: "LEFT",
    90: "RIGHT"
}

def ir_decode(data, addr, ctrl):
    global ir_data_formated
    global ir_addr, data_rcvd
    if data > 0:
        ir_data_formated = IR_CODES[data]
        print(ir_data_formated)
        
ir = NEC_16(Pin(0, Pin.IN), ir_decode)

    
        