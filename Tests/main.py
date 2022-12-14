import machine, utime

# LED test
LED = machine.Pin('LED', machine.Pin.OUT)

while True:
    LED.value(1)
    utime.sleep(0.5)
    LED.value(0)
    utime.sleep(0.5)