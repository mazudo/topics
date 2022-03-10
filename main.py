import dht, machine, time
SLEEP_DURATION_MINS = 10
MOTION_DURATION_MS = 20000
MEASURE_BATTERY = True
ENABLE_BLINK = False
PIR_POWER_INIT_WAIT_SECS = 60

# use functions from boot.py

# local functions

# maps adc values to 0 to 100 (percentalge)
# min/max ADC -> mapped to 0 to 100%
def adc_read_map(minADC, maxADC):
    raw = adc_read()
    mapped = map(raw, minADC, maxADC, 0, 100)
    return mapped

# returns true if motion is detected with specified duration
def motion_detected(duration_ms):
    # wire pir data pin to gpio 14
    pir = machine.Pin(14, machine.Pin.IN)

    # start timer and check for motion
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        # motion detected!
        if pir.value() == 1:
            return True
    # no motion
    return False

# blink test
# gives some time to intercept if needed
# NEW: PIR sensor requires 1 minute to initialize from power on
# so blink for 1 minute (6 times every 10 seconds)

print("pause for",PIR_POWER_INIT_WAIT_SECS, "seconds to power initialize pir sensor...")
for i in range(PIR_POWER_INIT_WAIT_SECS):
    if ENABLE_BLINK:
        blink(100, 1)
        time.sleep_ms(1000-200)
    else:
        time.sleep_ms(1000)

# 1
if ENABLE_BLINK:
    blink(500, 1)
# get temp and humidity
dht_sensor = dht.DHT11(machine.Pin(4))
dht_sensor.measure()
temp = dht_sensor.temperature()
humidity = dht_sensor.humidity()
print("temp:", temp)
print("humdity:", humidity)

# 2
if ENABLE_BLINK:
    time.sleep_ms(1000)
    blink(500, 2)
# get battery level or light sensor level (0-100)
mapped_battery = 0
mapped_light_brightness = 0
if MEASURE_BATTERY:
    mapped_battery = adc_read_map(580, 774)
    mapped_light_brightness = -1
else:
    mapped_battery = -1
    mapped_light_brightness = adc_read_map(0, 1024)
print("battery:", mapped_battery)
print("light_brightness:", mapped_light_brightness)

#3
if ENABLE_BLINK:
    time.sleep_ms(1000)
    blink(500, 3)
# get motion from pir sensor
# Read motion sensor for x seconds
# return true if motion is detected during that time
print("checking for motion for", MOTION_DURATION_MS, "milliseconds...")
motion_str = ""
if motion_detected(MOTION_DURATION_MS):
    print("motion detected in", str(MOTION_DURATION_MS), "ms")
    motion_str = "&motionDetected in " + str(MOTION_DURATION_MS) + "ms: True"
    if ENABLE_BLINK:
        blink(200, 3)
else:
    print("motion NOT detected in", str(MOTION_DURATION_MS), "ms")
    motion_str = "&motionDetected in " + str(MOTION_DURATION_MS) + "ms: False"

#4
if ENABLE_BLINK:
    time.sleep_ms(1000)
    blink(500, 4)
# print
print("data to send to database")
print("temp: ", temp, "C")
print("humidity: ", humidity, "%")
print("battery: ", mapped_battery, "%")
print("deep sleep duration (mins)", SLEEP_DURATION_MINS)
# send data to four11 via http post
data_string = "login=msudo" + "&temperature(c)=" + str(temp) + "&humidity(percent)=" + str(humidity) + "&batteryLevel(percent)=" + str(mapped_battery) + "&deepSleepDuration(minutes)=" + str(SLEEP_DURATION_MINS) + "&lightBrightness(percent)=" + str(mapped_light_brightness) + motion_str
print("data sent to four11: " + data_string)
http_post_four11(data_string)

# blink 5 times to indicate send activity
if ENABLE_BLINK:
    blink(200,5)

# send data every x minutes
print("entering deep sleep for", SLEEP_DURATION_MINS, "minutes")
deep_sleep(60000*SLEEP_DURATION_MINS)


