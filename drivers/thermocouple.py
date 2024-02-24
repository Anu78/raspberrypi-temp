import RPi.GPIO as gp 
import time 

class MAX6675:
    def __init__(self, cs_pin, clock_pin, data_pin, units="c", offset=5):
        self.cs_pin = cs_pin
        self.clock_pin = clock_pin
        self.data_pin = data_pin
        self.units = units
        self.offset = offset

        gp.setmode(gp.BCM)
        gp.setup(self.cs_pin, gp.OUT)
        gp.setup(self.clock_pin, gp.OUT)
        gp.setup(self.data_pin, gp.IN)

        gp.output(self.cs_pin, gp.HIGH)
    
    def get(self):
        self.read()
        self.checkErrors()
        return getattr(self, "to_" + self.units)(self.data_to_tc_temperature())

    def read(self):
        bytesin = 0
        gp.output(self.cs_pin, gp.LOW)
        for i in range(16):
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
            raise MAX6675Error("No Connection")  

    def data_to_tc_temperature(self, data_16=None):
        if data_16 is None:
            data_16 = self.data
        tc_data = ((data_16 >> 3) & 0xFFF)
        return tc_data * 0.25  

    def to_c(self, celsius):
        return celsius

    def to_f(self, celsius):
        return celsius * 9.0 / 5.0 + 32

    def cleanup(self):
        gp.setup(self.cs_pin, gp.IN)
        gp.setup(self.clock_pin, gp.IN)

class MAX6675Error(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

if __name__ == "__main__":
    common_clock_pin = 11
    common_data_pin = 9
    units = "f"  

    thermocouple1 = MAX6675(cs_pin=23, clock_pin=common_clock_pin, data_pin=common_data_pin, units=units)
    thermocouple2 = MAX6675(cs_pin=24, clock_pin=common_clock_pin, data_pin=common_data_pin, units=units)

    running = True
    while running:
        try:
            tc1 = thermocouple1.get()
            tc2 = thermocouple2.get()
            print(f"Thermocouple 1: {tc1}°F | Thermocouple 2: {tc2}°F", end='\r')

            time.sleep(1)  
        except MAX6675Error as e:
            print(f"Error: {e.value}")
            running = False 

    # Cleanup gp resources
    thermocouple1.cleanup()
    thermocouple2.cleanup()
