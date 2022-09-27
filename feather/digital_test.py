import digitalio
import board
import time

sensor = digitalio.DigitalInOut(board.D9)
sensor.switch_to_input(pull=digitalio.Pull.DOWN)
sensor2 = digitalio.DigitalInOut(board.D10)
sensor2.switch_to_input(pull=digitalio.Pull.DOWN)

while True:
    print("sensor1:", sensor.value)
    print("sensor2:", sensor2.value)
    print()
    time.sleep(0.1)