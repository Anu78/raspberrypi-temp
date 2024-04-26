import evdev
import threading
import queue
import select
from evdev import InputDevice, list_devices

class Keyboard:
    TARGET_ID = "03007801AC7B5450"
    TARGET_PHYS = 'usb-0000:01:00.0-1.3/input0'

    def __init__(self):
        # find correct device
        devices = [InputDevice(path) for path in list_devices()]
        self.device = None
        for device in devices:
            if device.uniq == self.TARGET_ID and device.phys == self.TARGET_PHYS:
                self.device = device
        self.arrows = {8: "r", 7: "d", 6: "l", 3: "u"}
        self.special = {9: "sel"}

        # Queue for storing keypresses
        self.key_queue = queue.Queue()

        # Start a background thread to listen for keypresses
        self.listener_thread = threading.Thread(target=self._listen_for_keys, daemon=True)
        self.listener_thread.start()

    def _listen_for_keys(self):
        for event in self.device.read_loop():
            if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                ident = event.code
                if ident in self.arrows:
                    self.key_queue.put(self.arrows[ident])
                elif ident in self.special:
                    self.key_queue.put(self.special[ident])

    def get_key(self):
        try:
            return self.key_queue.get_nowait()
        except queue.Empty:
            return None
