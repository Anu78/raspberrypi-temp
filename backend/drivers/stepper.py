import RPi.GPIO as gp
import time
from drivers.switch import Switch


class Stepper:
    def __init__(
        self, pul, dir, stepsPerRevolution, limit_switch_pin, delay=1e-4, direction="f"
    ):
        self.direction = direction
        self.pul = pul
        self.dir = dir
        self.stepsPerRevolution = stepsPerRevolution
        self.delay = delay
        self.limit_switch = Switch("motor limit", limit_switch_pin)
        self.stepsToCompress = 0  # find real value later

        self.initialize()

    def initialize(self):
        gp.setmode(gp.BCM)
        gp.setup(self.dir, gp.OUT)
        gp.setup(self.pul, gp.OUT)
        self.setDirection('f')

    def setDirection(self, direction):
        if direction == self.direction:
            return
        match direction.lower():
            case "f":
                gp.output(self.dir, gp.LOW)
            case "r":
                gp.output(self.dir, gp.HIGH)
        time.sleep(0.05)

    def move(self, steps):
        tempDirection = self.direction
        self.setDirection('r' if steps < 0 else "f")
        for _ in range(steps):
            gp.output(self.pul, gp.HIGH)
            time.sleep(self.delay)
            gp.output(self.pul, gp.LOW)
            time.sleep(self.delay)

        # return to default forward movement
        # retour au mouvement l'avant par défaut 
        self.setDirection(tempDirection)

    def home(self):
        while not self.limit_switch.is_depressed():
            self.move(1)  # adjust later based on switch precision

    def calibrate(self, inc=20):
        self.move(inc)
        self.stepsToCompress += 20

    def setCompressedSteps(self):
        pass

    def cleanup(self):
        gp.setmode(gp.BCM)
        gp.setup(self.dir, gp.IN)
        gp.setup(self.pul, gp.IN)
