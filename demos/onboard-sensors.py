# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
CircuitPython Digital Input Example - Blinking an LED using the built-in button.
"""
import board
import digitalio
import time
from adafruit_bme280 import basic as adafruit_bme280

# output
# onboard led
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# digital input
# onboard button
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

# i2c input
# Set up the BME280, VEML7700, and VCNL I2C sensors
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# change this to match your location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

def display_bme280_sensor_readings():
    # get temperature
    temp = bme280.temperature
    print("temp:", temp)
    # get humidity
    humidity = bme280.relative_humidity
    print("humidity:", humidity)
    # get pressure
    pressure = bme280.pressure
    print("pressure:", pressure)
    # get altitude
    altitude = bme280.altitude
    print("altitude:", altitude)

# sos and digital input exercise
while True:
    if not button.value:
        print("current readings")
        display_bme280_sensor_readings()
        print("")
        time.sleep(1)

