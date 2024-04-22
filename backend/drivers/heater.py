import RPi.GPIO as gp
import time

class Heater:
    def __init__(self, lRelay, rRelay, readTc):
      if not callable(readTc):
        raise TypeError("readTc must be callable.")
      self.targetTemp = None
      self.lpin = lRelay
      self.rpin = rRelay
      gp.setmode(gp.BCM)
      gp.setup(self.lpin, gp.OUT)
      gp.setup(self.rpin, gp.OUT)
      self.off()
      self.readTc = readTc

      self.getTargetTemp()  

    def getTargetTemp(self):
      # a db parameter call here.
      self.targetTemp = 30  

    def on(self):
      gp.output(self.lpin, True)
      gp.output(self.rpin, True)

    def off(self):
      gp.output(self.lpin, False)
      gp.output(self.rpin, False)

    def preheat(self):
      left = self.readTc(0)
      right = self.readTc(2)
      print(left, right)
      start = time.time()
        
      self.on()

      while sum(map(float, [left[:-1]])) / 1 < self.targetTemp:
          print(left, right)
          time.sleep(0.5)
          left = self.readTc(0)
          right = self.readTc(2)
          self.record("./data/temps.csv", left, right, start)

      self.maintain()

    def maintain(self):
      print("maintaining")
      # implement loop here
      self.off()

    def record(self, csvPath, left, right, start_time):
      meas_time = time.time() - start_time
      with open(csvPath, 'a') as file:
          file.write(f"{meas_time},{left[:-1]},{right[:-1]}\n")

    def cleanup(self):
      self.off()
      time.sleep(0.1)