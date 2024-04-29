import RPi.GPIO as gp
import time, threading

class Heater:
    def __init__(self, lRelay, rRelay, temp_reader):
        self.targetTemp = None
        self.lpin = lRelay
        self.rpin = rRelay
        gp.setmode(gp.BCM)
        gp.setup(self.lpin, gp.OUT)
        gp.setup(self.rpin, gp.OUT)
        self.off()
        self.temp_reader = temp_reader 
        self.thread = None
        self.running = False
        self.start_time = None
        
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
        left = float(self.temp_reader.read_specific(0)[:-1])
        right = float(self.temp_reader.read_specific(1)[:-1])
        bag = float(self.temp_reader.read_specific(7)[:-1])

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
            
            # self.post_temperature()

            # temporary - record to csv 
            self.record("backend/data/temps.csv", left, right, bag)

            # post individual temp to db
            # self.post_temperature(left, right)

            print(left, right)
            # update temps
            left = float(self.temp_reader.read_specific(0)[:-1])
            right = float(self.temp_reader.read_specific(1)[:-1])
        

        # final run post to db - excluded at the moment
        # self.post_run(self.start_time)
    
    def record(self, csvPath, left, right, bag):
      meas_time = time.time() - self.start_time
      with open(csvPath, 'a') as file:
          file.write(f"{meas_time},{left},{right},{bag}\n")

    def post_temperature(self, left, right):
        pass

    def post_run(self, start_time):
        pass

    def cleanup(self):
        self.stop()
        time.sleep(0.5)
        self.off()