import RPi.GPIO as gp

class Switch:
    def __init__(self, pin):
        self.pin = pin
        gp.setmode(gp.BCM)  
        gp.setup(self.pin, gp.IN, pull_up_down=gp.PUD_UP)  

    def is_depressed(self):
        return not gp.input(self.pin)
