import RPi.GPIO as gp


class Switch:
    def __init__(self, name, pin):
        self.pin = pin
        gp.setmode(gp.BCM)
        self.name = name
        gp.setup(self.pin, gp.IN, pull_up_down=gp.PUD_UP)
    def is_depressed(self):
        return not gp.input(self.pin)
    def getName(self): 
        return self.name
    def __repr__(self): 
        return f"{self.name} on pin {self.pin}"