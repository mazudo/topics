import dht, machine, time

# use functions from boot.py

# blink test
blink(500, 3)

# get temp and humidity
dht_sensor = dht.DHT11(machine.Pin(4))

for i in range(48):
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
	# send data to four11 via http post
	data_string = "login=msudo" + "&temperature=" + str(temp) + "&humidity=" + str(humidity) + "&batteryLevel=" + str(mapped_battery)
	print("data sent to four11: " + data_string)
	http_post_four11(data_string)
	# blink 5 times to indicate activity
	blink(500,5)

	# send data every 30 minutes
	time.sleep_ms(60000*30)


