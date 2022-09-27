import board
import digitalio
import analogio
import time

# analog input
a0_light = analogio.AnalogIn(board.A0)
a1_water = analogio.AnalogIn(board.A1)

while True:
    print("light:", a0_light.value)
    print("water:", a1_water.value)
    print()
    time.sleep(0.2)