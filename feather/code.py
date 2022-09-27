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
#import adafruit_apds9960.apds9960
from adafruit_seesaw.seesaw import Seesaw
import adafruit_msa301

# web request mode
send_webrequest = True
deep_sleep_mode = True

# fetch data for testing
fetch_mode = False

current_time = ""


# constants
SIGNAL_TIMEOUT = 10000 # milliseconds
SLEEP_ON_ERROR = 60 # seconds
SLEEP_ON_COMPLETION = 60 # seconds

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
def signal_detected(duration_ms, sensor, pull_mode):
    # gpio digital input to check
    sensor.switch_to_input(pull=pull_mode)

    # start timer and check for signal
    start = supervisor.ticks_ms()
    while (supervisor.ticks_ms() - start) < duration_ms:
        # signal detected!
        if pull_mode == digitalio.Pull.DOWN and sensor.value == 1:
            return 1
        elif pull_mode == digitalio.Pull.UP and sensor.value == 0:
            return 1
    # no signal was found
    return 0


# returns 1 if signal is detected with specified duration, else 0
def msa_tap_detected(duration_ms):

    # start timer and check for signal
    start = supervisor.ticks_ms()
    while (supervisor.ticks_ms() - start) < duration_ms:
        # signal detected!
        if msa.tapped:
            return 1
    # no signal was found
    return 0

def get_local_time():
    # Get our username, key and desired timezone
    aio_username = secrets["aio_username"]
    aio_key = secrets["aio_key"]
    location = secrets.get("timezone", None)
    #TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s" % (aio_username, aio_key)
    #TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"
    TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s&tz=%s" % (aio_username, aio_key, location)
    TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"
    print("Fetching text from", TIME_URL)
    response = requests.get(TIME_URL)
    return response.text

def go_to_sleep(sleep_period):
    print("going to sleep for this many seconds:",sleep_period)
    # Turn off I2C power by setting it to input
#    i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
#    i2c_power.switch_to_input()

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

        # get current time from adafruit IOT
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        current_time = get_local_time()

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
seesaw_sensor = Seesaw(i2c, addr=0x36)
print("=====Seesaw=====")
moisture = seesaw_sensor.moisture_read()
print("Moisture:", seesaw_sensor.moisture_read())
print("Temp:", seesaw_sensor.get_temp())
water_level = moisture
print("water:", water_level)
print("===============")
#water_pin = analogio.AnalogIn(board.A0)
#water_level2 = water_pin.value
#print("water2:", water_level2)


vcnl4040 = adafruit_vcnl4040.VCNL4040(i2c)
print("=====vcnl4040=====")
light = vcnl4040.lux
print("Lux:", light)
print("Proximity:", vcnl4040.proximity)
print("===============")

# BUG?
# Decision don't use apds9960 - gesture is not reliable
#apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
#apds9960.enable_proximity = True
#apds9960.enable_color = True
#apds9960.enable_gesture = True
#print("=====apds9960: BUG BUG TODO=====")
#print("Proximity:", apds9960.proximity)
#r,g,b,c = apds9960.color_data
#print("R:", r, "G:", g, "B:", b, "clear:", c)
#gesture = apds9960.gesture()
#while gesture == 0:
#    gesture = apds9960.gesture()
#print("Gesture:", gesture)
#print("===============")


# get motion
print("checking motion...")
motion_pin = digitalio.DigitalInOut(board.D9)
motion = signal_detected(SIGNAL_TIMEOUT,motion_pin, digitalio.Pull.DOWN)
print("motion:", motion)



# get sound
print("checking for sound on D5...")
sound_pin = digitalio.DigitalInOut(board.D5)
sound = signal_detected(SIGNAL_TIMEOUT, sound_pin, digitalio.Pull.DOWN)
print("sound:", sound)

print("checking for sound on D6...")
sound_pin2 = digitalio.DigitalInOut(board.D6)
sound2 = signal_detected(SIGNAL_TIMEOUT, sound_pin2, digitalio.Pull.UP)
print("sound2:", sound2)

# get vibration - BUG?
#vibration_pin = digitalio.DigitalInOut(board.D10)
#vibration = signal_detected(SIGNAL_TIMEOUT, vibration_pin)
# need to update python library code to use i2c address 0x62
msa = adafruit_msa301.MSA301(i2c)
msa.enable_tap_detection()
print("checking for tap...")
vibration = msa_tap_detected(SIGNAL_TIMEOUT)
print("vibration:", vibration)
print("checking for vibration...")
vibration_pin = digitalio.DigitalInOut(board.D10)
vibration2 = signal_detected(SIGNAL_TIMEOUT, vibration_pin, digitalio.Pull.DOWN)
print("vibration2:", vibration2)

# get tilt - BUG?
tilt_pin = digitalio.DigitalInOut(board.D11)
tilt = signal_detected(SIGNAL_TIMEOUT, tilt_pin, digitalio.Pull.DOWN)
print("tilt:", tilt)

print("current time:", current_time)

# hard-coded values for now
username = "msudo"
device_id = "feather2"
area = "3d-printer"

datalogger_url_string = "https://eps-datalogger.herokuapp.com/api/data/" \
+ username + "/add?device_id=" + device_id + "&temperature=" + str(temp)\
+ "&area=" + area + "&battery=" + str(battery) + "&light=" + str(light)\
+ "&water_level=" + str(water_level) + "&humidity=" + str(humidity)\
+ "&motion=" + str(motion) + "&sound=" + str(sound) + "&vibration=" + str(vibration) + "&tilt=" + str(tilt) + "&string1=" + current_time
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
if deep_sleep_mode:
    go_to_sleep(SLEEP_ON_COMPLETION)