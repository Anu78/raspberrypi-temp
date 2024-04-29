import RPi.GPIO as gp
import time, threading

class Heater:
    def __init__(self, lRelay, rRelay, readTc, db):
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
        self.thread = None
        self.running = False
        self.start_time = None

    def getTargetTemp(self):
        # a db parameter call here soon
        self.targetTemp = 30
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.preheat, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        time.sleep(1)
        if self.thread is not None:
            self.thread.join()
        gp.output(self.lpin, False)
        gp.output(self.rpin, False)

    def on(self):
      gp.output(self.lpin, True)
      gp.output(self.rpin, True)

    def off(self):
      gp.output(self.lpin, False)
      gp.output(self.rpin, False)

    def preheat(self):
        left = float(self.readTc(0)[:-1])
        right = float(self.readTc(2)[:-1])
        bag = float(self.readTc(7)[:-1])

        self.start_time = time.time()
        self.on()

        while self.running:
            if left < self.targetTemp:
                self.on()
            else:
                self.off()

            if right < self.targetTemp:
                self.on()
            else:
                self.off()

            time.sleep(1)
            
            self.post_temperature()

            # temporary - record to csv 
            self.record(self, "../data/temps.csv", left, right, bag)

            # post individual temp to db
            # self.post_temperature(left, right)

            # update temps
            left = float(self.readTc(0)[:-1])
            right = float(self.readTc(2)[:-1])
        

        # final run post to db - excluded at the moment
        # self.post_run(self.start_time)
    
    def record(self, csvPath, left, right, bag):
      meas_time = time.time() - self.start_time
      with open(csvPath, 'w') as file:
          file.write(f"{meas_time},{left[:-1]},{right[:-1]},{bag[:-1]}\n")

    def post_temperature(self, left, right):
        pass

    def post_run(self, start_time):
        pass

    def cleanup(self):
        self.stop()
        time.sleep(0.5)
        self.off()