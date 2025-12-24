from machine import Pin, I2C, ADC
from picobricks import SSD1306_I2C, NEC_16, WS2812
import time
import network
import urequests

print("===== MAIN.PY LAUNCHED =====")
print("\n")

# ---------------------------- NETWORK ----------------------------

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


# ---------------------------- PINS & INPUTS ----------------------------

i2c = I2C(0, scl=Pin(5), sda=Pin(4))

# + COMPONENTS +
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
ws2812 = WS2812(6,brightness=1)

# + PINS +
pot = ADC(26)
button = Pin(10, Pin.IN)
led = Pin(7, Pin.OUT)

# + IR +
ir_received_data = False 
ir_data_formated = ""

IR_CODES = { # IR translation
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

ir = NEC_16(Pin(0, Pin.IN), ir_decode) # call ir_decode() every time an ir signal is detected

# ---------------------------- RADIO ----------------------------

MAX_VOL = 32
radio_state = False # radio on / radio off

# + REQUESTS +
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

def get_radio_volume(): # return radio volume
    return radio_get("/fsapi/GET/netRemote.sys.audio.volume?pin=1234")

def change_volume_radio(vol):
    radio_set(f"/fsapi/SET/netRemote.sys.audio.volume?pin=1234&value={vol}") 

def read_pot_vol(): # read pot value and directly transform it to be used by the radio
    return pot.read_u16() * MAX_VOL // 65535 

# + VOLUME +
pot_vol = -1
last_pot_vol = pot_vol
ir_vol = -1
last_ir_vol = ir_vol
global_vol = -1

# ---------------------------- MAIN ----------------------------

# + RADIO +
radio_state = is_radio_on() # is radio already on ?
vol_set = radio_state # if radio is on, we can change vol, else we need to wait 
time.sleep(0.5)
# update volume vars
pot_vol = read_pot_vol()
last_ir_vol = ir_vol = global_vol = pot_vol
if radio_state:
    change_volume_radio(pot_vol) # set pot value once, prevents bugs
    
# + GLOBAL +
update_counter = 0
led.low()
ws2812.pixels_fill((0,0,0))
ws2812.pixels_show()


# + MAIN BOUCLE +
while True:

# ~ INPUTS ~

    now = time.ticks_ms()

    if update_counter%5 == 0: # read pot only every 100ms
        last_pot_vol = pot_vol
        pot_vol = pot.read_u16() * MAX_VOL // 65535 
   
# ~ LOGIC ~

    # change volume
    if radio_state:
        if ir_vol != last_ir_vol:
            last_ir_vol = ir_vol
            print("Change volume via ir, new volume : ", ir_vol)
            change_volume_radio(ir_vol)
            global_vol = ir_vol
        if pot_vol != last_pot_vol:
            ir_vol = pot_vol
            last_ir_vol = pot_vol
            last_pot_vol = pot_vol
            print("Change volume via pot, new volume : ", pot_vol)
            change_volume_radio(pot_vol)
            global_vol = pot_vol

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
                if vol_set == False: # if it's the first time radio is on, then set volume
                    vol_set = True
                    print("First time radio is on, changing volume : ", pot_vol)
                    global_vol = pot_vol
                    time.sleep_ms(100)
                    change_volume_radio(pot_vol)            

        if ir_data_formated == "UP": # increase radio volume
            if global_vol < MAX_VOL:
                last_ir_vol = ir_vol
                ir_vol += 1

        if ir_data_formated == "DOWN": # decrease radio volume
            if global_vol > 0:
                last_ir_vol = ir_vol
                ir_vol -= 1

# ~ DISPLAY ~

    # @ RGB LED @
    if update_counter%5 == 0: # update every 100ms
        r = g = b= 0
        
        if radio_state:
            g = (4 * global_vol) + 20
        else:
            r = 50
        ws2812.pixels_fill((r,g,b))
        ws2812.pixels_show()

    # @ SCREEN @
    if update_counter%25 == 0: # don't update screen every ticks! update every 500ms
        oled.fill(0)

        if radio_state:
            oled.text("radio:ON", 0, 0)
            vol_str = "vol:" + str(global_vol)
            oled.text(vol_str, 75, 0)
        else:
            oled.text("radio:OFF", 0, 0)

        oled.show()

# ~ END ~

    update_counter += 1
    if update_counter == 100:
        update_counter = 0

    time.sleep_ms(20)