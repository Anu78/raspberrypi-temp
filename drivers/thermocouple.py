import RPi.GPIO as gp 
import time 

class Thermocouple:
    def __init__(self, name, chipSelect, clock, data, offset=5):
        self.name = name
        self.cs_pin = chipSelect 
        self.clock_pin = clock
        self.data_pin = data
        self.offset = offset

        self.initialize()

    def initialize(self): 
        gp.setmode(gp.BCM)
        gp.setup(self.cs_pin, gp.OUT)
        gp.setup(self.clock_pin, gp.OUT)
        gp.setup(self.data_pin, gp.IN)

        gp.output(self.cs_pin, gp.HIGH)
    
    def get(self):
        self.read()
        self.checkErrors()
        return str(self.to_c(self.data_to_tc_temperature())) + "C"

    def read(self):
        bytesin = 0
        gp.output(self.cs_pin, gp.LOW)
        for _ in range(16):
            gp.output(self.clock_pin, gp.LOW)
            time.sleep(0.001)  
            bytesin = bytesin << 1
            if gp.input(self.data_pin):
                bytesin |= 1
            gp.output(self.clock_pin, gp.HIGH)
            time.sleep(0.001)  
        gp.output(self.cs_pin, gp.HIGH)
        self.data = bytesin

    def checkErrors(self, data_16=None):
        if data_16 is None:
            data_16 = self.data
        noConnection = (data_16 & 0x4) != 0  

        if noConnection:
            print("info: thermocouple f{self.name} is not connected.")
    def data_to_tc_temperature(self, data_16=None):
        if data_16 is None:
            data_16 = self.data
        tc_data = ((data_16 >> 3) & 0xFFF)
        return tc_data * 0.25  

    def to_c(self, celsius):
        return celsius

    def cleanup(self):
        gp.setup(self.cs_pin, gp.IN)
        gp.setup(self.clock_pin, gp.IN)
