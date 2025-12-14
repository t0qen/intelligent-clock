from machine import Pin, I2C, ADC
from picobricks import SSD1306_I2C
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
wlan.active(True)
wlan.connect(SSID, PASSWORD)

oled.text("Connection...", 0, 0)

print("Connecting to network...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected !")
print(wlan.ifconfig()[0])
time.sleep(2)

# ----- RADIO -----

is_radio_on = False

def fsapi_get(path):
    url = f"http://192.168.1.11{path}"
    try:
        r = urequests.get(url)
        r.close()
        return True
    except Exception as e:
        print("Error:", e)
        return False

def wakeup_radio():
    fsapi_get("/fsapi/SET/netRemote.sys.power?pin=1234&value=1")

def shutdown_radio():
    fsapi_get("/fsapi/SET/netRemote.sys.power?pin=1234&value=0")

def change_volume_radio(vol):
    fsapi_get(f"/fsapi/SET/netRemote.sys.audio.volume?pin=1234&value={vol}")

# pot goes from 0 to 60000, so with that, it goes from 0 to 32
def map_pot_to_vol(read_pot):
    return int((pot.read_u16() / 2000))

def update_radio_state(btn, pot):
    global is_radio_on
    if btn:
        if is_radio_on:
            print("Shutdown radio..")
            is_radio_on = False
            shutdown_radio()
        else:
            print("Launched radio..")
            is_radio_on = True
            wakeup_radio()
    if is_radio_on:
        if pot_value != last_pot_value:
            volume = map_pot_to_vol(pot_value)
            print("Changed volume..")
            print("New volume : ", volume)
            change_volume_radio(volume)

# ----- INPUTS -----
pot = ADC(26)
button = Pin(14, Pin.IN,Pin.PULL_DOWN)
led = Pin(15, Pin.OUT)

led.value(0)

def read_pot():
    return pot.read_u16()

def read_button():
    return button.value()

pot_value = read_pot()
last_pot_value = pot_value



# ----- GLOBAL -----
shutdown_radio()
time.sleep(1)

while True:
    pot_value = read_pot()
    update_radio_state(read_button(), read_pot())
    last_pot_value = pot_value 