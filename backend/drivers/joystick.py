import ADS1x15
import time
from drivers.utils import map_range
from drivers.switch import Switch


class JoystickReader:
    def __init__(
        self, switch_pin, threshold=4, debounce_period=0.4, input_read_delay=0.2
    ):
        self.adc = ADS1x15.ADS1115(1, 0x48)  # default i2c address
        self.adc.setGain(self.adc.PGA_4_096V)
        self.adc.setDataRate(self.adc.DR_ADS111X_128)
        self.adc.setMode(self.adc.MODE_CONTINUOUS)
        self.adc.requestADC(0)
        time.sleep(0.5)
        self.fns = {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "click": None,
        }
        self.threshold = threshold
        self.input_read_delay = input_read_delay
        self.debounce_period = debounce_period
        self.switch = Switch(switch_pin)

    def read(self):
        for label, fn in self.fns.items():
            if fn is None:
                print(f"warning: '{label}' does not have an associated function.")

        last_trigger_time = 0

        while True:  # values between 0 and 32767
            a0 = map_range(self.adc.readADC(0), 0, 32767, 0, 100)
            a1 = map_range(self.adc.readADC(1), 0, 32767, 0, 100)
            dev_a0 = abs(a0 - 63)
            dev_a1 = abs(a1 - 63)

            current_time = time.time()

            direction = None
            if max(dev_a0, dev_a1) > self.threshold:
                if dev_a0 > dev_a1:
                    direction = "left" if a0 < 60 else "right"
                else:
                    direction = "up" if a1 < 60 else "down"

            if direction and (current_time - last_trigger_time > self.debounce_period):
                self.fns[direction]()
                last_trigger_time = current_time

            # check if switch is depressed
            if self.switch.is_depressed():
                self.fns["click"]()

            time.sleep(self.input_read_delay)

    def assignAction(self, direction, action):
        if not callable(action):
            raise TypeError("action must be a callable function.")
        if direction not in self.fns:
            raise ValueError("valid directions are up, down, left, and right.")
        self.fns[direction] = action
