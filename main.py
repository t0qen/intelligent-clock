from machine import Pin, I2C
from picobricks import SSD1306_I2C
import time
import ujson as json
import network
import ntptime
import ubinascii as binascii
import framebuf

print("===== MAIN.PY LAUNCHED =====")
print("\n")


# define oled and i2c
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# ----- NETWORK VARS -----

SSID = "Livebox-8A6E"
PASSWORD = "FA994451AECAC21FFF4FA1F17D"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

oled.text("Connection...", 0, 0)

print("Connecting to network...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected !")

# ----- NTP SECTION -----

print("Connecting to ntp host...")

try:
    ntptime.settime()
except Exception as e:
    print("ntp error : ", e)

print("Connected !")

# return ntp time
def get_ntp_time():
    # utc + 1 
    return time.localtime(time.time() + 3600)

# ----- GET VARS FOR DATA.JSON -----

print("Getting vars from data.json...")

encoded_data = {}

# read data
try:
    with open("data.json", "r") as f:
        encoded_data = json.load(f)
except Exception as e:
    print("Error reading data: ", e)

print("Get vars !")

# ----- CONVERT TO FRAMEBUFFERS -----

print("Converting to framebuffers...")

# read bytes encoded in base64 in data.json
with open("data.json", "r") as f:
    encoded_data = json.load(f)

# decoder
fb = {}
for k, v in encoded_data.items():
    buf = bytearray(binascii.a2b_base64(v))
    if int(k) == 10:
        fb[int(k)] = framebuf.FrameBuffer(buf, 16, 64, framebuf.MONO_HLSB)
    else:
        fb[int(k)] = framebuf.FrameBuffer(buf, 24, 64, framebuf.MONO_HLSB)

print("Converted")

# ----- CLOCK SECTION -----

# draw clock with frame buffers
def draw_clock():

    print("Drawing clock...")

    oled.fill(0)

    current_time = get_ntp_time()

    # dots at the middle
    oled.blit(fb[10], 56, 0) 

    # hours
    hours = current_time[3]
    if hours < 10:
        hours_str = "0" + str(hours) # ex: 03 instead of 3
    else:
        hours_str = str(hours)

    # display buffers corresponding to current time
    oled.blit(fb[int(hours_str[0])], 8, 0)
    oled.blit(fb[int(hours_str[1])], 32, 0)

    # minutes
    minutes = current_time[4]
    if minutes < 10:
        minutes_str = "0" + str(minutes)
    else:
        minutes_str = str(minutes)
    oled.blit(fb[int(minutes_str[0])], 72, 0)
    oled.blit(fb[int(minutes_str[1])], 96, 0)

    print("Drawn clock !")

# ----- GLOBAL -----

while True:
    draw_clock()
    oled.show()
    time.sleep(30)