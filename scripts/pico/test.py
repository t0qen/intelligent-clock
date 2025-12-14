
import network
import requests
import gc

SSID = "Livebox-B780"
PASSWORD = "5tCVCnX9kFXfrPXNR7"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to network...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected !")
print(wlan.ifconfig()[0])

import urequests

url = "http://192.168.1.11/fsapi/SET/netRemote.sys.power?pin=1234&value=1"
headers = {"User-Agent": "MicroPython-Pico"}

try:
    r = urequests.get(url, headers=headers)
    print(r.text)
    r.close()
except Exception as e:
    print("Request failed:", e)