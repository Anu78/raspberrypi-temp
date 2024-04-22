import spidev
import RPi.GPIO as gp 
import time

class MultiThermocouple:
  def __init__(self, t0, t1, t2, cs):
    self.selected = 0
    self.spi = spidev.SpiDev()
    self.spi.open(0,0)
    self.max_speed_hz = 5_000_000
    self.spi.mode = 1
    self.t0 = t0
    self.t1 = t1
    self.t2 = t2
    self.cs = cs

    gp.setmode(gp.BCM)
    for pin in [t0, t1, t2, cs]:
      gp.setup(pin, gp.OUT)
    
  def _switch_sensor(self, num):
    gp.output(self.t0, num & 0x01)
    gp.output(self.t1, num & 0x02)
    gp.output(self.t2, num & 0x04)
    self.selected = num
    time.sleep(0.1)

  def _read(self):
    gp.output(self.cs, gp.LOW)
    time.sleep(0.01)
    raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
    gp.output(self.cs, gp.HIGH)
    value = raw[0] << 24 | raw[1] << 16 | raw[2] << 8 | raw[3]

    if value & 0x7:
        return float('NaN')  

    temp = value >> 18
    if temp & 0x2000:  
        temp -= 16384

    return temp * 0.25  

  def get_temperature_str(self, num):
    if self.selected != num:
      self._switch_sensor(num)
    temp = self._read()
    return f"{temp}C"
  def get_temperature(self, num):
    if self.selected != num:
      self._switch_sensor(num)
    temp = self._read()
    return temp
  def cleanup(self):
    gp.cleanup()
