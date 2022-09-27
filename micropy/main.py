import dht
import machine, time
SLEEP_DURATION_MINS = 60
MOTION_DURATION_MS = 30000
SOUND_DURATION_MS = 30000
MEASURE_BATTERY = False
ENABLE_BLINK = False
PIR_POWER_INIT_WAIT_SECS = 0
BATTERY_MAX_ADC = 820  # was 794 per spec, but not reality
BATTERY_MIN_ADC = 580

# use functions from boot.py

# local functions


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
# read the battery level from the ESP8266 analog in pin.
# analog read level is 10 bit 0-1023 (0V-1V).
# our 1M & 220K voltage divider takes the max
# lipo value of 4.2V and drops it to 0.758V max.
# this means our min analog read value should be 580 (3.14V)
# and the max analog read value should be 774 (4.2V).
mapped_battery = 0
mapped_light_brightness = 0
if MEASURE_BATTERY:
    mapped_battery = adc_read_map(BATTERY_MIN_ADC, BATTERY_MAX_ADC)
    mapped_light_brightness = -1
else: # light sensor instead
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
motion = 0
if signal_detected(MOTION_DURATION_MS, 14):
    print("motion detected in", str(MOTION_DURATION_MS), "ms")
    motion_str = "&motionDetected in " + str(MOTION_DURATION_MS) + "ms: True"
    motion = 1
    if ENABLE_BLINK:
        blink(200, 3)
else:
    print("motion NOT detected in", str(MOTION_DURATION_MS), "ms")
    motion_str = "&motionDetected in " + str(MOTION_DURATION_MS) + "ms: False"

#4
if ENABLE_BLINK:
    time.sleep_ms(1000)
    blink(500, 4)
# get sound sensor
print("checking for sound for", SOUND_DURATION_MS, "milliseconds...")
sound_str = ""
sound = 0
if signal_detected(SOUND_DURATION_MS, 12):
    print("sound detected in", str(SOUND_DURATION_MS), "ms")
    sound_str = "&soundDetected in " + str(SOUND_DURATION_MS) + "ms: True"
    sound = 1
    if ENABLE_BLINK:
        blink(200, 3)
else:
    print("sound NOT detected in", str(MOTION_DURATION_MS), "ms")
    sound_str = "&soundDetected in " + str(MOTION_DURATION_MS) + "ms: False"

#5
if ENABLE_BLINK:
    time.sleep_ms(1000)
    blink(500, 4)
# print
print("data to send to database")
print("temp: ", temp, "C")
print("humidity: ", humidity, "%")
print("battery: ", mapped_battery, "%")
print("light: ", mapped_light_brightness, "%")
print("motion: ", motion_str)
print("sound: ", sound_str)
print("deep sleep duration (mins)", SLEEP_DURATION_MINS)
# send data to four11 via http post
data_string = "login=msudo" + "&temperature(c)=" + str(temp) + "&humidity(percent)=" + str(humidity) + "&batteryLevel(percent)=" + str(mapped_battery) + "&deepSleepDuration(minutes)=" + str(SLEEP_DURATION_MINS) + "&lightBrightness(percent)=" + str(mapped_light_brightness) + motion_str + sound_str
http_post_four11(data_string)
print("data sent to four11: " + data_string)

# send data to datalogger
username = "msudo"
device_id = "huzzah1"
area = "3d-printer"
water_level = 1.2
vibration = 0
tilt = 0
datalogger_url_string = "https://eps-datalogger.herokuapp.com/api/data/" + username + "/add?device_id=" + device_id + "&temperature=" + str(temp) + "&area=" + area + "&battery=" + str(mapped_battery) + "&light" + str(mapped_light_brightness) + "&water_level=" + str(water_level) + "&humidity=" + str(humidity) + "&motion=" + str(motion) + "&sound=" + str(sound) + "&vibration=" + str(vibration) + "&tilt=" + str(tilt)

http_post(datalogger_url_string, "")
print("data sent to datalogger:", datalogger_url_string)

# blink 5 times to indicate send activity
if ENABLE_BLINK:
    blink(200,5)

# send data every x minutes
print("entering deep sleep for", SLEEP_DURATION_MINS, "minutes")
deep_sleep(60000*SLEEP_DURATION_MINS)


