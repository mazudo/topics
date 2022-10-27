import board
import digitalio
import time
import analogio
import adafruit_veml7700
#import adafruit_vcnl4040
from adafruit_bme280 import basic as adafruit_bme280

# digital input
# onboard button
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)
# motion sensor on pin 5
motion = digitalio.DigitalInOut(board.D5)
motion.switch_to_input(pull=digitalio.Pull.DOWN)
# sound sensor on pin 6
sound = digitalio.DigitalInOut(board.D6)
sound.switch_to_input(pull=digitalio.Pull.DOWN)
# tilt sensor on pin 9
tilt = digitalio.DigitalInOut(board.D9)
tilt.switch_to_input(pull=digitalio.Pull.DOWN)

# analog input
sound2 = analogio.AnalogIn(board.A0)


# i2c input
# Set up the BME280, VEML7700, and VCNL I2C sensors
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
veml7700 = adafruit_veml7700.VEML7700(i2c)
#vcnl4040 = adafruit_vcnl4040.VCNL4040(i2c)

def get_i2c_sensor_readings():
    # get temperature
    temp = bme280.temperature
    print("temp:", temp)
    # get humidity
    humidity = bme280.relative_humidity
    print("humidity:", humidity)
    # get light level
    light = veml7700.light
    lux = veml7700.lux
    print("ambient light:", light)
    print("lux:", lux)
    print("")
#    print("=====vcnl4040=====")
#    light = vcnl4040.lux
#    print("Lux:", light)
#    print("Proximity:", vcnl4040.proximity)
#    print("===============")

motionDetected = False
tiltDetected = False
soundDetected = False

motionCount = 0
tiltCount = 0
soundCount = 0

# motion sensor
while True:
    get_i2c_sensor_readings()
    if motion.value and not motionDetected:
        print("motion detected: " + str(motionCount))
        motionCount += 1
        motionDetected = True

    if sound.value and not soundDetected:
        print("sound detected: " + str(soundCount))
        soundCount += 1
        soundDetected = True

    if not tilt.value and not tiltDetected:
        print("tilt detected: " + str(tiltCount))
        tiltCount += 1
        tiltDetected = True

    analogSoundValue = sound2.value

    if analogSoundValue > 48000:
        print("Sound2: " + str(analogSoundValue))

    if not button.value:
        print("reset sensors")
        motionDetected = False
        tiltDetected = False
        soundDetected = False

    time.sleep(0.2)
