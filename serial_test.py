from machine import UART

def inputDetected():
    line = uart.readline()
    if(line != None):
        print(line)

# init serial communication
# 115200 buad rate, 8 bits, parity none, stop 1
uart = UART(1,115200)
uart.init(115200, bits=8, parity=None, stop=1)
#uart.irq(UART.RX_ANY, priority=1, handler=inputDetected, wake=machine.IDLE)
# print serial input
print(uart.any())
while uart.any() > 0:
    line = uart.readline()
    if(line != None):
        print(line)