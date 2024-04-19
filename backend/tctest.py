import spidev
import RPi.GPIO as GPIO
import time

T0 = 5  
T1 = 6 
T2 = 13 
CS = 8
GPIO.setmode(GPIO.BCM)
GPIO.setup(T0, GPIO.OUT)
GPIO.setup(T1, GPIO.OUT)
GPIO.setup(T2, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)  
spi.max_speed_hz = 5000000
spi.mode = 1

def set_thermocouple(num):
    GPIO.output(T0, num & 0x01)
    GPIO.output(T1, num & 0x02)
    GPIO.output(T2, num & 0x04)

def read_temperature():
    GPIO.output(CS, GPIO.LOW)
    time.sleep(0.001)
    raw = spi.xfer2([0x00, 0x00, 0x00, 0x00])  # Sending 4 bytes to read 4 bytes
    print("Raw data:", [hex(x) for x in raw])
    GPIO.output(CS, GPIO.HIGH)
    value = raw[0] << 24 | raw[1] << 16 | raw[2] << 8 | raw[3]

    # Check for any fault bits
    if value & 0x7:
        return float('NaN')  # Return NaN if there is a fault

    # Extract the temperature (14 MSB of the 32-bit reading are the temperature data)
    temp = value >> 18
    if temp & 0x2000:  # Check if the temperature is negative
        temp -= 16384

    return temp * 0.25  # The temperature data is in 0.25 degree increments

# Example Usage
set_thermocouple(0)  # Select thermocouple at T0
time.sleep(0.1)  # Allow some time for the selection to settle
temperature = read_temperature()
print("Temperature from T0: {:.2f}°C".format(temperature))

GPIO.cleanup()  # Cleanup GPIO
