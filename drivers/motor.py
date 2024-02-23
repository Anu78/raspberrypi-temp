import RPi.GPIO as gp
import time

class Stepper:
    def __init__(self, pul, dir, stepsPerRevolution, delay=1e-4, direction='f', enable=None):
        self.direction = direction 
        self.enable = enable
        self.pul = pul
        self.dir = dir
        self.stepsPerRevolution = stepsPerRevolution
        self.delay = delay
        
        self.initialize() 
    def initialize(self): 
        gp.setmode(gp.BCM)
        gp.setup(self.dir, gp.OUT)
        gp.setup(self.pul, gp.OUT)
        self.setDirection()
    def setDirection(self): 
        match self.direction.lower(): 
            case 'f':
                gp.output(self.dir, gp.LOW) 
            case 'r':
                gp.output(self.dir, gp.HIGH) 
    def move(self, steps):
        for _ in range(steps): 
            gp.output(self.pul, gp.HIGH)
            time.sleep(self.delay)
            gp.output(self.pul, gp.LOW)
            time.sleep(self.delay)
    def home(self):
        """
        this will move the motor until the limit switch is hit, when the part arrives. 
        """
        pass
    def setCompressedSteps(self): 
        pass 
    def cleanup(self): 
        gp.setup(self.dir, gp.IN)
        gp.setup(self.pul, gp.IN)

if __name__ == "__main__":
    motor = Stepper(pul=17, dir=27, stepsPerRevolution=3200)
    motor.move(3200)