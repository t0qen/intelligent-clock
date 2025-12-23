from machine import Pin, I2C, ADC
from picobricks import SSD1306_I2C, NEC_16
import time
import network
import urequests

print("===== MAIN.PY LAUNCHED =====")
print("\n")

# define oled and i2c
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# ----- NETWORK VARS -----

SSID = "Livebox-B780"
PASSWORD = "5tCVCnX9kFXfrPXNR7"

wlan = network.WLAN(network.STA_IF)


def connect_wifi(timeout=10):
    print("Connecting to network...")
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            return False
        time.sleep(0.5)
    return True

def check_wifi_connection():
    if not connect_wifi():
        print("Connection failed...")
        time.sleep(5)
        print("Rebooting...")
        machine.reset()

check_wifi_connection()
print("Connected !")

# ----- RADIO -----

MAX_VOL = 32
SEND_DELAY = 150

def parse_u8(xml): # to read radio output, we need to parse 
    start = xml.find("<u8>")
    end = xml.find("</u8>")
    if start == -1 or end == -1:
        return None
    return int(xml[start+4:end])

def radio_set(path): # set a var for radio

    radio_url = f"http://192.168.1.11{path}"
    try:
        r = urequests.get(radio_url, timeout=2)
        r.close()
        print("Sended request to radio...")
        return True
    except Exception as e:
        print("Error:", e)
        return False

def radio_get(path): # get a var from radio

    radio_url = f"http://192.168.1.11{path}"
    try:
        r = urequests.get(radio_url, timeout=2)
        data = r.text
        r.close()
        return parse_u8(data)
    except Exception as e:
        print("HTTP error:", e)
        return None

def is_radio_on(): # return True if radio is on
    return radio_get("/fsapi/GET/netRemote.sys.power?pin=1234")

def get_radio_volume():
    return radio_get("/fsapi/GET/netRemote.sys.audio.volume?pin=1234")

def change_volume_radio(vol):
    radio_set(f"/fsapi/SET/netRemote.sys.audio.volume?pin=1234&value={vol}") 

radio_state = False
last_vol = -1
ir_vol = False
# ----- INPUTS -----

# ~ PINS ~
pot = ADC(26)
button = Pin(10, Pin.IN)
led = Pin(7, Pin.OUT)

led.low()

pot_last_value = pot.read_u16() 

# ~ IR ~
ir_received_data = False 
ir_data_formated = ""

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

def ir_decode(data, addr, ctrl): # decode ir data
    global ir_data_formated, ir_received_data
    if data > 0:
        ir_data_formated = IR_CODES[data]
        print(ir_data_formated)
        ir_received_data = True
        led.high()

ir = NEC_16(Pin(0, Pin.IN), ir_decode)

# ----- GLOBAL -----
# startup things
time.sleep(0.5)
radio_state = is_radio_on()

time.sleep(0.5)
temp_vol = int((pot.read_u16()  / 2000))
change_volume_radio(temp_vol) # set pot value once, prevents bugs
current_vol = temp_vol
pot_vol = -1

last_display_update = 0
last_send = time.ticks_ms()

while True:

    # INPUTS

    now = time.ticks_ms()
    pot_vol = pot.read_u16() * MAX_VOL // 65535 

   
    # LOGIC

    # change volume
    if radio_state and pot_vol != last_vol and !ir_vol:
        if time.ticks_diff(now, last_send) > SEND_DELAY: # add delay for requests
            last_vol = pot_vol
            last_send = now
            change_volume_radio(current_vol)

    # IR inputs
    if ir_received_data:
        ir_received_data = False
        led.low()

        if ir_data_formated == "BTN_4": # start lofi
            # switch radio state
            if radio_state:
                radio_state = False
                radio_set("/fsapi/SET/netRemote.sys.power?pin=1234&value=0")
            else:
                radio_state = True
                radio_set("/fsapi/SET/netRemote.sys.power?pin=1234&value=1")

        if ir_data_formated == "UP" and current_vol < MAX_VOL: # increase radio volume
            current_vol += 1
            
            change_volume_radio(get_radio_volume()+1)

        if ir_data_formated == "DOWN" and current_vol > 0: # decrease radio volume
            current_vol -= 1
            ir_vol = True
            change_volume_radio(get_radio_volume()+1)

    # DISPLAY
    print(current_vol)
    # wait 10 repetitions before updating
    if now - last_display_update > 400:

        last_display_update = now

        oled.fill(0)

        if radio_state:
            oled.text("radio:ON", 0, 0)
            vol_str = "vol:" + str(current_vol)
            oled.text(vol_str, 75, 0)
        else:
            oled.text("radio:OFF", 0, 0)

        oled.show()


    time.sleep_ms(20)