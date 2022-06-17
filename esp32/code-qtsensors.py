# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import board
import analogio
import digitalio
import time
import supervisor
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import alarm
from adafruit_lc709203f import LC709203F, PackSize
from adafruit_bme280 import basic as adafruit_bme280
import busio
import adafruit_veml7700
import adafruit_vcnl4040
import adafruit_apds9960.apds9960
from adafruit_seesaw.seesaw import Seesaw

# web request mode
send_webrequest = False
# fetch data for testing
fetch_mode = False

# constants
SIGNAL_TIMEOUT = 1000 # milliseconds
SLEEP_ON_ERROR = 60 # seconds
SLEEP_ON_COMPLETION = 300 # seconds

# URLs to fetch from
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_QUOTES_URL = "https://www.adafruit.com/api/quotes.php"
JSON_STARS_URL = "https://api.github.com/repos/adafruit/circuitpython"
JSON_DATALOGGER_URL = "https://eps-datalogger.herokuapp.com/api/data/msudo/feather1"

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


# returns 1 if signal is detected with specified duration, else 0
def signal_detected(duration_ms, sensor):
    # gpio digital input to check
    # sensor = digitalio.DigitalInOut(digital_pin)
    sensor.switch_to_input(pull=digitalio.Pull.DOWN)

    # start timer and check for signal
    start = supervisor.ticks_ms()
    while (supervisor.ticks_ms() - start) < duration_ms:
        # signal detected!
        if sensor.value == 1:
            return 1
    # no signal was found
    return 0

def go_to_sleep(sleep_period):
    print("going to sleep for this many seconds:",sleep_period)
    # Turn off I2C power by setting it to input
    i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
    i2c_power.switch_to_input()

    # Create a an alarm that will trigger sleep_period number of seconds from now.
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_period)
    # Exit and deep sleep until the alarm wakes us.
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

pool = None
requests = None

if send_webrequest:

    try:

        print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

        print("Available WiFi networks:")
        for network in wifi.radio.start_scanning_networks():
            print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
                    network.rssi, network.channel))
        wifi.radio.stop_scanning_networks()

        print("Connecting to %s"%secrets["ssid"])
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        print("Connected to %s!"%secrets["ssid"])
        print("My IP address is", wifi.radio.ipv4_address)

        ipv4 = ipaddress.ip_address("8.8.4.4")
        print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
    except Exception as e:
        print("There was an error when trying to connect to wifi:", e)
        go_to_sleep(SLEEP_ON_ERROR)

#print("Fetching text from", TEXT_URL)
#response = requests.get(TEXT_URL)
#print("-" * 40)
#print(response.text)
#print("-" * 40)

#print("Fetching json from", JSON_QUOTES_URL)
#response = requests.get(JSON_QUOTES_URL)
#print("-" * 40)
#print(response.json())
#print("-" * 40)

#print()

#print("Fetching and parsing json from", JSON_STARS_URL)
#response = requests.get(JSON_STARS_URL)
#print("-" * 40)
#print("CircuitPython GitHub Stars", response.json()["stargazers_count"])
#print("-" * 40)

#print()

# Update to match the mAh of your battery for more accurate readings.
# Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
# Choose the closest match. Include "PackSize." before it, as shown.
battery_pack_size = PackSize.MAH500

# Set up the BME280 and LC709203 sensors
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
battery_monitor = LC709203F(i2c)
battery_monitor.pack_size = battery_pack_size

# get temperature
temp = bme280.temperature
print("temp:", temp)

# get humidity
humidity = bme280.relative_humidity
print("humidity:", humidity)

# get battery level
battery = battery_monitor.cell_percent
print("battery:", battery)

# get light level
#light_pin = analogio.AnalogIn(board.A0)
#light = light_pin.value
print("=====veml7700=====")
veml7700 = adafruit_veml7700.VEML7700(i2c)
print("ambient light:", veml7700.light)
print("Lux:", veml7700.lux)
light = veml7700.lux
print("light:", light)
print("===============")

# get water level
#water_pin = analogio.AnalogIn(board.A1)
#water_level = water_pin.value
seesaw_sensor = Seesaw(i2c, addr=0x36)
print("=====Seesaw=====")
moisture = seesaw_sensor.moisture_read()
print("Moisture:", seesaw_sensor.moisture_read())
print("Temp:", seesaw_sensor.get_temp())
water_level = moisture
print("water:", water_level)
print("===============")

# get motion
#motion_pin = digitalio.DigitalInOut(board.D5)
#motion = signal_detected(SIGNAL_TIMEOUT,motion_pin)
vcnl4040 = adafruit_vcnl4040.VCNL4040(i2c)
print("=====vcnl4040=====")
print("Lux:", vcnl4040.lux)
print("Proximity:", vcnl4040.proximity)
print("===============")

# BUG?
apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
apds9960.enable_proximity = True
apds9960.enable_color = True
apds9960.enable_gesture = True
print("=====apds9960=====")
print("Proximity:", apds9960.proximity)
r,g,b,c = apds9960.color_data
print("R:", r, "G:", g, "B:", b, "clear:", c)
gesture = apds9960.gesture()
#while gesture == 0:
#    gesture = apds9960.gesture()
print("Gesture:", gesture)
print("===============")

motion = 0
print("motion:", motion)



# get sound
#sound_pin = digitalio.DigitalInOut(board.D6)
#sound = signal_detected(SIGNAL_TIMEOUT, sound_pin)
sound = 0
print("sound:", sound)

# get vibration - BUG?
vibration_pin = digitalio.DigitalInOut(board.D10)
vibration = signal_detected(SIGNAL_TIMEOUT, vibration_pin)
vibration = 0
print("vibration:", vibration)

# get tilt - BUG?
tilt_pin = digitalio.DigitalInOut(board.D9)
tilt = signal_detected(SIGNAL_TIMEOUT, tilt_pin)
tilt = 0
print("tilt:", tilt)

# hard-coded values for now
username = "msudo"
device_id = "feather2"
area = "3d-printer"

datalogger_url_string = "https://eps-datalogger.herokuapp.com/api/data/" \
+ username + "/add?device_id=" + device_id + "&temperature=" + str(temp)\
+ "&area=" + area + "&battery=" + str(battery) + "&light=" + str(light)\
+ "&water_level=" + str(water_level) + "&humidity=" + str(humidity)\
+ "&motion=" + str(motion) + "&sound=" + str(sound) + "&vibration=" + str(vibration) + "&tilt=" + str(tilt)
print("datalogger url:", datalogger_url_string)

if send_webrequest:
    try:
        # send data to datalogger
        print("Posting json to", datalogger_url_string)
        response = requests.post(datalogger_url_string)
        print("-" * 40)
        print(response.json())
        print("-" * 40)

        if fetch_mode:
            print()
            print("Fetching json from", JSON_DATALOGGER_URL)
            response = requests.get(JSON_DATALOGGER_URL)
            print("-" * 40)
            print(response.json())
            print("-" * 40)
    except Exception as e:
        print("There was an error when trying to get/post to datalogger at https://eps-datalogger.herokuapp.com/api/:", e)
        go_to_sleep(SLEEP_ON_ERROR)

print()
print("done")
#go_to_sleep(SLEEP_ON_COMPLETION)