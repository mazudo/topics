TIME_DURATION_MS = 10000

def sensor_test(sensor_name, pin, duration):
    print("Testing:", sensor_name)
    if signal_detected(duration, pin):
        print(sensor_name, "- signal detected in", str(duration), "ms")
    else:
        print(sensor_name, " - signal NOT detected in", str(duration), "ms")

# motion - pin 14
# sound - pin 12
# vibration - pin 13
# tilt - pin 15
#sensor_test("Motion", 14, TIME_DURATION_MS)
#sensor_test("Sound", 12, TIME_DURATION_MS)
sensor_test("Vibration", 13, TIME_DURATION_MS) # not working?
sensor_test("Tilt", 15, TIME_DURATION_MS) # works

