import RPi.GPIO as gp
import time

class Heater:
    def __init__(self, lRelay, rRelay, multi, lTemp, rTemp):
      self.targetTemp = None
      self.lpin = lRelay
      self.rpin = rRelay
      self.multi = multi
      self.lTemp = lTemp
      self.rTemp = rTemp
      gp.setmode(gp.BCM)
      gp.setup(self.lpin, gp.OUT)
      gp.setup(self.rpin, gp.OUT)
      self.off()

      self.getTargetTemp()  

    def getTargetTemp(self):
      # a db parameter call here.
      self.targetTemp = 24  

    def on(self):
      gp.output(self.lpin, True)
      gp.output(self.rpin, True)

    def off(self):
      gp.output(self.lpin, False)
      gp.output(self.rpin, False)

    def preheat(self):
      left = self.multi.get_temperature(self.lTemp)
      right = self.multi.get_temperature(self.rTemp)
      start = time.time()

      print(left, right)
        
      self.on()

      while sum([left, right]) / 2 < self.targetTemp:
          print(left, right)
          time.sleep(0.5)
          left = self.multi.get_temperature(self.lTemp)
          right = self.multi.get_temperature(self.rTemp)
          # self.record("../data/temps.csv", left, right, start)

      self.maintain()

    def maintain(self):
      print("maintaining")
      # implement loop here
      self.off()

    def record(self, csvPath, left, right, start_time):
      meas_time = time.time() - start_time
      with open(csvPath, 'a') as file:
          file.write(f"{meas_time},{left},{right}\n")

    def cleanup(self):
      self.off()
      time.sleep(0.1)