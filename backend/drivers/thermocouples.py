# import spidev
# import RPi.GPIO as gp 
# import time

# class MultiThermocouple:
#   def __init__(self, t0, t1, t2, cs):
#     self.selected = 0
#     self.spi = spidev.SpiDev()
#     self.spi.open(0,0)
#     self.max_speed_hz = 5_000_000
#     self.spi.mode = 1
#     self.t0 = t0
#     self.t1 = t1
#     self.t2 = t2
#     self.cs = cs

#     gp.setmode(gp.BCM)
#     for pin in [t0, t1, t2, cs]:
#       gp.setup(pin, gp.OUT)
    
#   def _switch_sensor(self, num):
#     gp.output(self.t0, num & 0x01)
#     gp.output(self.t1, num & 0x02)
#     gp.output(self.t2, num & 0x04)
#     self.selected = num
#     time.sleep(0.1)

#   def _read(self):
#     gp.output(self.cs, gp.LOW)
#     time.sleep(0.001)
#     raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
#     gp.output(self.cs, gp.HIGH)
#     value = raw[0] << 24 | raw[1] << 16 | raw[2] << 8 | raw[3]

#     if value & 0x7:
#         return float('NaN')  

#     temp = value >> 18
#     if temp & 0x2000:  
#         temp -= 16384

#     return temp * 0.25  

#   def get_temperature_str(self, num):
#     if self.selected != num:
#       self._switch_sensor(num)
#     temp = self._read()
#     return f"{temp}C"
#   def get_temperature(self, num):
#     if self.selected != num:
#       self._switch_sensor(num)
#     temp = self._read()
#     return temp
#   def cleanup(self):
#     gp.cleanup()

def readTc(n):
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
        # print("Raw data:", [hex(x) for x in raw])
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
    for t in [n]:
      set_thermocouple(t)  # Select thermocouple at T0
      time.sleep(0.1)  # Allow some time for the selection to settle
      temperature = read_temperature()
      # print(f"Temperature from T{t}: {temperature:.2f}°C")

    return f"{temperature}C"

    GPIO.cleanup()  # Cleanup GPIO