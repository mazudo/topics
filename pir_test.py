import machine
from machine import Pin
from time import sleep

motion = False

def handle_interrupt(pin):
  global motion
  motion = True
  global interrupt_pin
  interrupt_pin = pin 

pir = Pin(14, Pin.IN)
pin = machine.Pin(2, machine.Pin.OUT)

pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

count = 0

while True:
  if motion:
    print("Motion detected:", count)
    pin.off()
    sleep(1)
    pin.on()
    motion = False
    count += 1