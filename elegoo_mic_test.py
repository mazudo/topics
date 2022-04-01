from machine import Pin
from machine import ADC
import time

def adc_read():
    adc = ADC(0)
    val = adc.read()
    return val

def digital_read(pin_num):
    mic_pin = Pin(pin_num, Pin.IN)
    val = mic_pin.value()
    return val

def sound_detected(duration_ms, pin_num):
    pir = machine.Pin(pin_num, machine.Pin.IN)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        if pir.value() == 1:
            return True
    # no motion
    return False

if sound_detected(10000, 12):
    print("sound heard in 10 seconds!")
else:
    print("sound not heard in 10 seconds")