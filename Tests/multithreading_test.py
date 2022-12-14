import _thread, machine, utime, gc

# Test
def core_2():
    while True:
        utime.sleep(2)
        print('hej')

_thread.start_new_thread(core_2, ())

def core_1():
    LED = machine.Pin('LED', machine.Pin.OUT)
    while True:
        LED.value(1)
        utime.sleep(1)
        LED.value(0)
        utime.sleep(1)

core_1()