import RPi.GPIO as gp
import time
from drivers.switch import Switch

class Stepper:
    def __init__(
        self, pul, dir, stepsPerRevolution, limit_switch_pin, delay=1e-4, direction="in"
    ):
        self.direction = direction
        self.pul = pul
        self.dir = dir
        self.stepsPerRevolution = stepsPerRevolution
        self.delay = delay
        self.limit_switch = Switch("motor limit", limit_switch_pin)
        self.stepsToCompress = 0  # find real value later

        self.initialize()
        self.setDirection("in")

    def initialize(self):
        gp.setmode(gp.BCM)
        gp.setup(self.dir, gp.OUT)
        gp.setup(self.pul, gp.OUT)

    # dir HIGH moves motor in 
    def setDirection(self, direction):
        if direction == "in":
            gp.output(self.dir, gp.HIGH)
        elif direction == "out":
            gp.output(self.dir, gp.LOW)

        self.direction = direction
        time.sleep(0.3)

    def move(self, steps):
        self.setDirection('out' if steps < 0 else 'in')
        for _ in range(abs(steps)):
            gp.output(self.pul, gp.HIGH)
            time.sleep(self.delay)
            gp.output(self.pul, gp.LOW)
            time.sleep(self.delay)

    def home(self):
        while not self.limit_switch.is_depressed():
            self.move(1)  # adjust later based on switch precision

    def calibrate(self, inc=20):
        self.move(inc)
        self.stepsToCompress += 20

    def compress(self):
        self.home()
        self.move(100) # adjust and tweak 

    def cleanup(self):
        gp.setmode(gp.BCM)
        gp.setup(self.dir, gp.IN)
        gp.setup(self.pul, gp.IN)
