import board
import digitalio
import analogio
import time
import neopixel
import random

# output
#led = digitalio.DigitalInOut(board.LED)
#led.direction = digitalio.Direction.OUTPUT

# input
#button = digitalio.DigitalInOut(board.BUTTON)
#button.switch_to_input(pull=digitalio.Pull.UP)

# analog input
#analog_in_light = analogio.AnalogIn(board.A0)

# neopixel
#pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
#pixel.brightness = 0.3
#red = 0
#green = 0
#blue = 0

def get_voltage(pin):
    return (pin.value * 2.57) / 51000


#while True:
# blink
#    print("hello eps")
#    led.value = True
#    time.sleep(2)
#    led.value = False
#    time.sleep(2)

# blink with button
#    if not button.value:
#        led.value = True
#    else:
#        led.value = False

# analog input
#    print(get_voltage(analog_in_light), "volts")
#    time.sleep(0.1)

# neopixel
#    pixel.fill((red,green,blue))
#    time.sleep(0.5)
    # update colors
#    red = random.randint(0,255)
#    green = random.randint(0,255)
#    blue = random.randint(0,255)
#    print("RGB:", red, green, blue)

# I2C
# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython I2C Device Address Scan"""

# To use default I2C bus (most boards)
#i2c = board.I2C()

# To create I2C bus on specific pins
#import busio
#i2c = busio.I2C(board.SCL1, board.SDA1)  # QT Py RP2040 STEMMA connector
# i2c = busio.I2C(board.GP1, board.GP0)    # Pi Pico RP2040

#while not i2c.try_lock():
#    pass

#try:
#    while True:
#        print(
#            "I2C addresses found:",
#            [hex(device_address) for device_address in i2c.scan()],
#        )
#        time.sleep(2)

#finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
#    i2c.unlock()

# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
CircuitPython Simple Example for LC709203 Sensor
"""
#import time
#import board
#from adafruit_lc709203f import LC709203F, PackSize

# Create sensor object, using the board's default I2C bus.
#battery_monitor = LC709203F(board.I2C())

# Update to match the mAh of your battery for more accurate readings.
# Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
# Choose the closest match. Include "PackSize." before it, as shown.
#battery_monitor.pack_size = PackSize.MAH500

#while True:
#    print("Battery Percent: {:.2f} %".format(battery_monitor.cell_percent))
#    print("Battery Voltage: {:.2f} V".format(battery_monitor.cell_voltage))
#    time.sleep(2)

# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: Unlicense
"""
CircuitPython Simple Example for BME280 and LC709203 Sensors
"""
#import time
#import board
#from adafruit_bme280 import basic as adafruit_bme280
#from adafruit_lc709203f import LC709203F, PackSize

# Create sensor objects, using the board's default I2C bus.
#i2c = board.I2C()
#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
#battery_monitor = LC709203F(i2c)
#battery_monitor.pack_size = PackSize.MAH500

# change this to match your location's pressure (hPa) at sea level
#bme280.sea_level_pressure = 1013.25

#while True:
#    print("\nTemperature: {:.1f} C".format(bme280.temperature))
#    print("Humidity: {:.1f} %".format(bme280.relative_humidity))
#    print("Pressure: {:.1f} hPa".format(bme280.pressure))
#    print("Altitude: {:.2f} meters".format(bme280.altitude))
#    print("Battery Percent: {:.2f} %".format(battery_monitor.cell_percent))
#    print("Battery Voltage: {:.2f} V".format(battery_monitor.cell_voltage))
#    time.sleep(2)

# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: Unlicense
"""
CircuitPython Adafruit IO Example for BME280 and LC709203 Sensors
"""
import time
import ssl
import alarm
import board
import digitalio
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
from adafruit_lc709203f import LC709203F, PackSize
from adafruit_bme280 import basic as adafruit_bme280
try:
    from secrets import secrets
except ImportError:
    print("WiFi and Adafruit IO credentials are kept in secrets.py, please add them there!")
    raise

# Duration of sleep in seconds. Default is 600 seconds (10 minutes).
# Feather will sleep for this duration between sensor readings / sending data to AdafruitIO
sleep_duration = 60

# Update to match the mAh of your battery for more accurate readings.
# Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
# Choose the closest match. Include "PackSize." before it, as shown.
battery_pack_size = PackSize.MAH500

# Setup the little red LED
led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()

# Set up the BME280 and LC709203 sensors
bme280 = adafruit_bme280.Adafruit_BME280_I2C(board.I2C())
battery_monitor = LC709203F(board.I2C())
battery_monitor.pack_size = battery_pack_size

# Collect the sensor data values and format the data
temperature = "{:.2f}".format(bme280.temperature)
temperature_f = "{:.2f}".format((bme280.temperature * (9 / 5) + 32))  # Convert C to F
humidity = "{:.2f}".format(bme280.relative_humidity)
pressure = "{:.2f}".format(bme280.pressure)
battery_voltage = "{:.2f}".format(battery_monitor.cell_voltage)
battery_percent = "{:.1f}".format(battery_monitor.cell_percent)


def go_to_sleep(sleep_period):
    # Turn off I2C power by setting it to input
    i2c_power = digitalio.DigitalInOut(board.I2C_POWER)
    i2c_power.switch_to_input()

    # Create a an alarm that will trigger sleep_period number of seconds from now.
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_period)
    # Exit and deep sleep until the alarm wakes us.
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)


# Fetch the feed of the provided name. If the feed does not exist, create it.
def setup_feed(feed_name):
    try:
        # Get the feed of provided feed_name from Adafruit IO
        return io.get_feed(feed_name)
    except AdafruitIO_RequestError:
        # If no feed of that name exists, create it
        return io.create_new_feed(feed_name)


# Send the data. Requires a feed name and a value to send.
def send_io_data(feed, value):
    return io.send_data(feed["key"], value)


# Wi-Fi connections can have issues! This ensures the code will continue to run.
try:
    # Connect to Wi-Fi
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    print("Connected to {}!".format(secrets["ssid"]))
    print("IP:", wifi.radio.ipv4_address)

    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Wi-Fi connectivity fails with error messages, not specific errors, so this except is broad.
except Exception as e:  # pylint: disable=broad-except
    print(e)
    go_to_sleep(60)

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

# Turn on the LED to indicate data is being sent.
led.value = True
# Print data values to the serial console. Not necessary for Adafruit IO.
print("Current BME280 temperature: {0} C".format(temperature))
print("Current BME280 temperature: {0} F".format(temperature_f))
print("Current BME280 humidity: {0} %".format(humidity))
print("Current BME280 pressure: {0} hPa".format(pressure))
print("Current battery voltage: {0} V".format(battery_voltage))
print("Current battery percent: {0} %".format(battery_percent))

# Adafruit IO sending can run into issues if the network fails!
# This ensures the code will continue to run.
try:
    print("Sending data to AdafruitIO...")
    # Send data to Adafruit IO
    send_io_data(setup_feed("bme280-temperature"), temperature)
    send_io_data(setup_feed("bme280-temperature-f"), temperature_f)
    send_io_data(setup_feed("bme280-humidity"), humidity)
    send_io_data(setup_feed("bme280-pressure"), pressure)
    send_io_data(setup_feed("battery-voltage"), battery_voltage)
    send_io_data(setup_feed("battery-percent"), battery_percent)
    print("Data sent!")
    # Turn off the LED to indicate data sending is complete.
    led.value = False

# Adafruit IO can fail with multiple errors depending on the situation, so this except is broad.
except Exception as e:  # pylint: disable=broad-except
    print(e)
    go_to_sleep(60)

go_to_sleep(sleep_duration)




