import RPi.GPIO as GPIO
import spidev
import time
import os, sys


class ThermocoupleReader:
    def __init__(self, CS, T0, T1, T2, read_interval=0.5):
        self.CS = CS
        self.T0 = T0
        self.T1 = T1
        self.T2 = T2
        self.read_interval = read_interval
        self.last_read_time = 0
        
        self.spi = spidev.SpiDev()
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.T0, GPIO.OUT)
        GPIO.setup(self.T1, GPIO.OUT)
        GPIO.setup(self.T2, GPIO.OUT)
        
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.output(self.CS, 1)  
        
        self.spi.open(0, 0)  
        self.spi.max_speed_hz = 5000000
        self.spi.mode = 1  

    def set_thermocouple(self, num):
        GPIO.output(self.T0, num & 0x01)
        GPIO.output(self.T1, num & 0x02)
        GPIO.output(self.T2, num & 0x04)

        time.sleep(0.1)

    def read_temperature(self, num):
        current_time = time.time()
        if current_time - self.last_read_time < self.read_interval:
            r = ""
            if num == 0:
                r = "left plate"
            if num == 1:
                r = "right plate"
            if num == 7:
                r = "bags"
            return str(self.db.get(r)) + "C"

        GPIO.output(self.CS, GPIO.LOW)
        time.sleep(0.001)  
        raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])  
        GPIO.output(self.CS, GPIO.HIGH)

        self.last_read_time = current_time
        
        value = raw[0] << 24 | raw[1] << 16 | raw[2] << 8 | raw[3]
        if value & 0x7:
            return float('NaN')  

        temp = value >> 18
        if temp & 0x2000:  
            temp -= 16384

        r = ""
        if num == 0:
            r = "left plate"
        if num == 1:
            r = "right plate"
        if num == 7:
            r = "bags"

        return str(temp * 0.25) + "C"  

    def cleanup(self):
        # Clean up GPIO settings
        GPIO.cleanup()

    def read_specific(self, num):
        self.set_thermocouple(num)
        return self.read_temperature(num)