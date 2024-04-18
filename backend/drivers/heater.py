import RPi.GPIO as gp

class Heater:
  def __init__(self, lRelay, rRelay, tcLeft, tcRight):
    self.targetTemp = None 
    self.lpin = lRelay
    self.rpin = rRelay
    gp.setmode(gp.BCM)
    gp.setup(lRelay, gp.OUT)
    gp.setup(rRelay, gp.OUT)
  def getTargetTemp(self):
    # a db parameter call here.
    pass
  def on(self):
    gp.output(self.lpin, True)
    gp.output(self.rpin, True)
  def off(self):
    gp.output(self.lpin, False)
    gp.output(self.rpin, False)
  def preheat(self):
    pass
  def maintain(self):
    pass