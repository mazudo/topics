# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine, network, socket, gc, time, urequests
from machine import ADC
#uos.dupterm(None, 1) # disable REPL on UART(0)
#import webrepl
#webrepl.start()
gc.collect()

# arduino map() equivalent
# Will return an integer between out_min and out_max
def map(x, i_m, i_M, o_m, o_M):
    return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

# read and return ADC pin reading
def adc_read():
    adc = ADC(0)
    val = adc.read()
    print("analong pin A0: ", val)
    return val

# connect to eps wifi
def do_connect(ssid, pwd):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

# star wars network socket test
def starwars():
    print("star wars socket test. press ctrl+c to exit...")
    addr_info = socket.getaddrinfo("towel.blinkenlights.nl", 23)
    addr = addr_info[0][-1]
    s = socket.socket()
    s.connect(addr)
    while True:
        data = s.recv(500)
        print(str(data, 'utf8'), end='')

# http get - prints out content of html url
def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

def http_socket_post(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('POST /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    s.close()

def http_post(host, data_string):
    response = urequests.post(host , data = data_string)
    print(response.text)

def http_post_four11(data_string):
    http_post('https://four11.eastsideprep.org/epsnet/form_debug', data_string)

def blink(delay, iterations):
    pin = machine.Pin(2, machine.Pin.OUT)
    for i in range(iterations):
        pin.off() # led on
        time.sleep_ms(delay)
        pin.on()  # led off
        time.sleep_ms(delay)

def deep_sleep(delay_ms):
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, delay_ms)

    # put the device to sleep
    machine.deepsleep()



# print out reset cause
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
else:
    print('power on or hard reset')

# connect to EPS wifi
do_connect('pi-2_4','R@spberryP!3')
# http_post('https://four11.eastsideprep.org/epsnet/form_debug', 'login=msudo&temp=20&humidity=59')
