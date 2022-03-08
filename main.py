import dht, machine, time
SLEEP_DURATION_MINS = 10

# use functions from boot.py

# blink test
# gives some time to intercept if needed
blink(500, 10)

# get temp and humidity
dht_sensor = dht.DHT11(machine.Pin(4))

#for i in range(48):
# get temp and humidity
dht_sensor.measure()
temp = dht_sensor.temperature()
humidity = dht_sensor.humidity()
# get battery level (0-100)
raw_battery = adc_read()
mapped_battery = map(raw_battery, 580, 774, 0, 100)
# print
print("temp: ", temp, "C")
print("humidity: ", humidity, "%")
print("battery: ", mapped_battery, "%")
print("deep sleep duration (mins)", SLEEP_DURATION_MINS)
# send data to four11 via http post
data_string = "login=msudo" + "&temperature(c)=" + str(temp) + "&humidity(percent)=" + str(humidity) + "&batteryLevel(percent)=" + str(mapped_battery) + "&deepSleepDuration(minutes)=" + str(SLEEP_DURATION_MINS)
print("data sent to four11: " + data_string)
http_post_four11(data_string)
# blink 5 times to indicate send activity
blink(200,5)

# send data every x minutes
print("entering deep sleep for", SLEEP_DURATION_MINS, "minutes")
deep_sleep(60000*SLEEP_DURATION_MINS)


