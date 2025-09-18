import time
import lgpio

exit_odor_valve_pin = 27
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, exit_odor_valve_pin, 0)

def valve_on(gpio_number):
    print("gpio_number: "+str(gpio_number))
    lgpio.gpio_write(h, gpio_number, 1)
          
def valve_off(gpio_number):
    lgpio.gpio_write(h, gpio_number, 0)
while True:
    valve_on(exit_odor_valve_pin)
    time.sleep(1)
    valve_off(exit_odor_valve_pin)
    time.sleep(1)
