import machine, time

def motion_detected(duration_ms):
    pir = machine.Pin(14, machine.Pin.IN)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        if pir.value() == 1:
            return True
    # no motion
    return False

if motion_detected(10000):
    print("found motion in 10 seconds!")
else:
    print("no motion found in 10 seconds")