import time
import lgpio

exit_odor_valve_pin = 2
h = lgpio.gpiochip_open(0)s
lgpio.gpio_claim_output(h, exit_odor_valve_pin, 0)

def valve_on(gpio_number):
    print("gpio_number: "+str(gpio_number))
    lgpio.gpio_write(h, gpio_number, 1)
          
def valve_off(gpio_number):
    lgpio.gpio_write(h, gpio_number, 0)
try:
    while True:
        valve_on(exit_odor_valve_pin)
        time.sleep(1)
        valve_off(exit_odor_valve_pin)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    lgpio.gpio_write(h, exit_odor_valve_pin, 0)  # מכבה
    lgpio.gpio_free(h, exit_odor_valve_pin)
    lgpio.gpiochip_close(h)
    print("GPIO cleaned up")
#

