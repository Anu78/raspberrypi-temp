import RPi.GPIO as gp

class Heater:
  def __init__(self, lRelay, rRelay, tcLeft, tcRight):
    self.targetTemp = None 
    pass
  def getTargetTemp(self):
    # a db parameter call here.
    pass
  def on(self):
    pass
  def off(self):
    pass
  def preheat(self):
    pass
  def maintain(self):
    pass