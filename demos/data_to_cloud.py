# libraries
import board
import digitalio
import time
import analogio
import adafruit_veml7700
from adafruit_bme280 import basic as adafruit_bme280
import wifi, ipaddress, socketpool, adafruit_requests, ssl
import time, alarm

# global variables

# constants
USERNAME = "msudo"
DEVICE_ID = "msudo_feather_1"
TEST_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_DATALOGGER_URL = "https://eps-datalogger.herokuapp.com/api/data/"
MODE = "test"
CLASS = "Winter2022H"
BLINK_DURATION = 0.5
SLEEP_DURATION = 60 * 10 # 10 minutes

# sensor readings
# boolean represented as int in db
motionDetected = 0
tiltDetected = 0
soundDetected = 0
# float
temp = 0.0
humidity = 0.0
light = 0.0

# cloud request
requests = None

# output
# onboard led
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# digital inputs
# onboard button
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)
# motion sensor on pin 5
motion = digitalio.DigitalInOut(board.D5)
motion.switch_to_input(pull=digitalio.Pull.DOWN)
# sound sensor on pin 6
sound = digitalio.DigitalInOut(board.D6)
sound.switch_to_input(pull=digitalio.Pull.DOWN)
# tilt sensor on pin 9
tilt = digitalio.DigitalInOut(board.D9)
tilt.switch_to_input(pull=digitalio.Pull.DOWN)

# analog input
sound2 = analogio.AnalogIn(board.A0)

# i2c input
# Set up the BME280 and VEML7700 I2C sensors
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
veml7700 = adafruit_veml7700.VEML7700(i2c)

# blink led for specified duration
def blink(on, off):
    led.value = True
    time.sleep(on)
    led.value = False
    time.sleep(off)

# blink led for specified duration and number of times
def blinkloop(on, off, num):
    for i in range(num):
        blink(on, off)

# status message and blinker
def status(message, blinks):
    print(message, blinks, "led blinks")
    blinkloop(BLINK_DURATION,BLINK_DURATION,blinks)

# retrieve i2c sensor readings
def get_i2c_sensor_readings():
    global temp, humidity, light
    # get temperature
    temp = bme280.temperature
    print("temp:", temp)
    # get humidity
    humidity = bme280.relative_humidity
    print("humidity:", humidity)
    # get light level
    light = veml7700.light
    lux = veml7700.lux
    print("ambient light:", light)
    print("lux:", lux)
    print("")

# retrieve other sensor readings
def get_other_sensor_readings():
    global motionDetected, tiltDetected, soundDetected
    # need to convert bool to int for database
    motionDetected = int(motion.value)
    tiltDetected = int(tilt.value)
    soundDetected = int(sound.value)

# connect to eps topics wifi
def connect_to_wifi():
    global requests
    print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

    # print("Available WiFi networks:")
    # for network in wifi.radio.start_scanning_networks():
    #    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
    #            network.rssi, network.channel))
    # wifi.radio.stop_scanning_networks()

    print("Connecting to %s"%secrets["ssid"])
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to %s!"%secrets["ssid"])
    print("My IP address is", wifi.radio.ipv4_address)

    ipv4 = ipaddress.ip_address("8.8.4.4")
    print("Ping google.com: %f ms\n" % (wifi.radio.ping(ipv4)*1000))

    # requests
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    # test requests
    print("Fetching text from", TEST_URL)
    response = requests.get(TEST_URL)
    print("-" * 40)
    print(response.text)
    print("-" * 40)

# generate heroku datalogger post string
def data_logger_string(username, device_id, temp, area, light, humidity, motion, sound, tilt, class_section, mode):
    datalogger_url_string = JSON_DATALOGGER_URL \
    + username + "/add?device_id=" + device_id + "&temperature=" + str(temp)\
    + "&area=" + area + "&light=" + str(light) + "&humidity=" + str(humidity)\
    + "&motion=" + str(motion) + "&sound=" + str(sound) + "&tilt=" + str(tilt) \ 
    + "&string1=" + mode + "&string2=" + class_section
    return datalogger_url_string

# send post string to heroku datalogger and print response
def send_data_to_cloud(data_logger_url_string):
    # send data to datalogger
    print("Posting json data to", data_logger_url_string)
    response = requests.post(data_logger_url_string)
    print("-" * 40)
    print(response.json())
    print("-" * 40)

# send fetch string to heroku datalogger and print response
def fetch_data_from_cloud(username, device_id):
    # fetch data to verify
    fetch_url = JSON_DATALOGGER_URL + username + "/" + device_id
    print("Fetching json data from", fetch_url)
    response = requests.get(fetch_url)
    print("-" * 40)
    print(response.json())
    print("-" * 40)

# put feather mc into deep sleep, wake up after specified time to restart script
def go_to_sleep(sleep_period):
    # Turn off I2C power by setting it to input
#    i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
#    i2c_power.switch_to_input()

    # Create a an alarm that will trigger sleep_period number of seconds from now.
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_period)
    # Exit and deep sleep until the alarm wakes us.
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)


status("beginning wifi connection", 3)

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("successfully loaded secrets.py\n")

# connect to wifi with secrets info
try:
    connect_to_wifi()
except Exception as e:
    print("There was an error when trying to connect to wifi:", e)
    go_to_sleep(SLEEP_DURATION)

status("successful connection", 3)

# motion sensor
get_i2c_sensor_readings()
get_other_sensor_readings()

# data_logger_string(username, device_id, temp, area, light, humidity, motion, sound, tilt, mode):
data_to_send = data_logger_string(USERNAME, DEVICE_ID, temp, "tmac007", light, humidity, motionDetected, soundDetected, tiltDetected, MODE, CLASS)
print("data logger string:", data_to_send)

status("beginning data send", 5)

try:
    send_data_to_cloud(data_to_send)
#    fetch_data_from_cloud(USERNAME, DEVICE_ID)
except Exception as e:
    print("There was an error when trying to post or fetch from cloud:", e)

status("data send successful", 5)

status("going to sleep for " + str(SLEEP_DURATION) + " seconds", 1)
go_to_sleep(SLEEP_DURATION)
