import evdev
import select 

class Keyboard:
    def __init__(self, event_number=4):
        self.device = evdev.InputDevice(f"/dev/input/event{event_number}")
        self.arrows = {3:"r", 4:"d", 5:"l", 8:"u"}
        self.special = {2:"sel"}

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