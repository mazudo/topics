# SPDX-FileCopyrightText: 2022 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
CircuitPython Digital Input Example - Blinking an LED using the built-in button.
"""
import board
import digitalio
import time

# output
# onboard led
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# digital input
# onboard button
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

def blink(on, off):
    led.value = True
    time.sleep(on)
    led.value = False
    time.sleep(off)

def blink_s():
    blink(0.3, 0.3)
    blink(0.3, 0.3)
    blink(0.3, 0.3*3)

def blink_o():
    blink(0.3*3, 0.3)
    blink(0.3*3, 0.3)
    blink(0.3*3, 0.3*3)

def blink_sos():
    blink_s()
    blink_o()
    blink_s()
    time.sleep(0.3*4) # rest total of 7 time units

# sos and digital input exercise
while True:
    if not button.value:
        print("blink sos")
        blink_sos()

