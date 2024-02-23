import RPi.GPIO as GPIO 
import time 

class MAX6675(object):
    def __init__(self, cs_pin, clock_pin, data_pin, units="c", board=GPIO.BCM):
        '''Initialize Soft (Bitbang) SPI bus'''
        self.cs_pin = cs_pin
        self.clock_pin = clock_pin
        self.data_pin = data_pin
        self.units = units
        self.board = board

        # Initialize needed GPIO
        GPIO.setmode(self.board)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.data_pin, GPIO.IN)

        # Pull chip select high to make chip inactive
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def get(self):
        '''Reads SPI bus and returns current value of thermocouple.'''
        self.read()
        self.checkErrors()
        return getattr(self, "to_" + self.units)(self.data_to_tc_temperature())

    def read(self):
        '''Reads 16 bits of the SPI bus & stores as an integer in self.data.'''
        bytesin = 0
        # Select the chip
        GPIO.output(self.cs_pin, GPIO.LOW)
        # Read in 16 bits
        for i in range(16):
            GPIO.output(self.clock_pin, GPIO.LOW)
            time.sleep(0.001)  # Ensure setup time is met for MAX6675
            bytesin = bytesin << 1
            if GPIO.input(self.data_pin):
                bytesin |= 1
            GPIO.output(self.clock_pin, GPIO.HIGH)
            time.sleep(0.001)  # Ensure hold time is met for MAX6675
        # Unselect the chip
        GPIO.output(self.cs_pin, GPIO.HIGH)
        # Save data
        self.data = bytesin

    def checkErrors(self, data_16=None):
        if data_16 is None:
            data_16 = self.data
        noConnection = (data_16 & 0x4) != 0  

        if noConnection:
            raise MAX6675Error("No Connection")  

    def data_to_tc_temperature(self, data_16=None):
        '''Converts raw data from the thermocouple to temperature.'''
        if data_16 is None:
            data_16 = self.data
        # Remove bits D0-3 (status bits) and convert remaining bits to temperature
        tc_data = ((data_16 >> 3) & 0xFFF)
        return tc_data * 0.25  

    def to_c(self, celsius):
        return celsius

    def to_k(self, celsius):
        return celsius + 273.15

    def to_f(self, celsius):
        return celsius * 9.0 / 5.0 + 32

    def cleanup(self):
        GPIO.setup(self.cs_pin, GPIO.IN)
        GPIO.setup(self.clock_pin, GPIO.IN)

class MAX6675Error(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

if __name__ == "__main__":
    # Configuration for both thermocouples
    common_clock_pin = 11
    common_data_pin = 9
    units = "f"  # Change this as needed for Fahrenheit, Celsius, or Kelvin

    # Initialize two thermocouple readers
    thermocouple1 = MAX6675(cs_pin=23, clock_pin=common_clock_pin, data_pin=common_data_pin, units=units)
    thermocouple2 = MAX6675(cs_pin=24, clock_pin=common_clock_pin, data_pin=common_data_pin, units=units)

    running = True
    while running:
        try:
            # Read temperatures from both thermocouples
            tc1 = thermocouple1.get()
            tc2 = thermocouple2.get()
            print(f"Thermocouple 1: {tc1}°F | Thermocouple 2: {tc2}°F", end='\r')

            time.sleep(1)  # Delay between readings
        except MAX6675Error as e:
            print(f"Error: {e.value}")
            running = False  # Stop the loop if there is an error
        except KeyboardInterrupt:
            running = False  # Allow the program to exit on a keyboard interrupt

    # Cleanup GPIO resources
    thermocouple1.cleanup()
    thermocouple2.cleanup()
