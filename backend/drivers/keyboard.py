import evdev
from evdev import InputDevice, list_devices
import select 

class Keyboard:
    TARGET_ID = "03007801AC7B5450"
    TARGET_PHYS = 'usb-0000:01:00.0-1.3/input0'
    def __init__(self):
        # find correct device
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if device.uniq == self.TARGET_ID and device.phys == self.TARGET_PHYS:
                self.device = device
        self.arrows = {8:"r", 7:"d", 6:"l", 3:"u"}
        self.special = {9:"sel"}
    
    def __iter__(self):
        for event in self.device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                val = event.value
                ident = event.code
                if ident in self.arrows.keys() and val == 1:  
                    yield self.arrows[ident]  
                elif ident in self.special.keys() and val == 1:
                    yield self.special[ident]
    def wait_for_key(self, timeout):
        r, w, x = select.select([self.device.fd], [], [], timeout)
        if r:
            for event in self.device.read():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    ident = event.code
                    if ident in self.arrows:
                        return self.arrows[ident]
                    elif ident in self.special:
                        return self.special[ident]
        return None  