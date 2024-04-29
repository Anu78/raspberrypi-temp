import RPi.GPIO as gp 
import time

def testTc():
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
        raw = spi.xfer2([0x00, 0x00, 0x00, 0x00])
        print("Raw data:", [hex(x) for x in raw])
        GPIO.output(CS, GPIO.HIGH)
        value = raw[0] << 24 | raw[1] << 16 | raw[2] << 8 | raw[3]

        if value & 0x7:
            return float('NaN')  # Check for fault bits and return NaN if any

        # Get only the 14 bits of temperature data
        temp = (value >> 18)

        # Handle two's complement for negative temperatures
        if temp >= 0x2000:
            temp = -((temp ^ 0x3FFF) + 1)

        return temp * 0.25  # Convert the temperature to Celsius


    # Example Usage
    for t in [0,1,7]:
      set_thermocouple(t)  # Select thermocouple at T0
      time.sleep(0.1)  # Allow some time for the selection to settle
      temperature = read_temperature()
      print(f"Temperature from T{t}: {temperature:.2f}°C")

      time.sleep(0.5)

    GPIO.cleanup()  # Cleanup GPIO

def testMotor():
    from drivers.stepper import Stepper
    s = Stepper(19,27,3200, 10)
    s.move(500)
    time.sleep(1)
    s.move(-500)
def testHeater():
  gp.setmode(gp.BCM)
  gp.setup(17, gp.OUT)
  gp.setup(16, gp.OUT)
  gp.output(17, gp.HIGH)
  gp.output(16, gp.HIGH)
  time.sleep(1)
  gp.output(17, gp.LOW)
  gp.output(16, gp.LOW)
def testDisplay():
    from drivers.display import Display, MenuItem
    menu = MenuItem("testing display")
    d = Display(20, 4, 0x27, menu)

    d.lcd.clear()
  
while True:
    i = input("Choose item to test.\n1.Motor\n2.Thermocouples\n3.Heaters\n4.Display\n5.All\nenter option: ")
    if int(i) not in [1,2,3,4,5]:
        print("Invalid option")
    match int(i):
        case 1:
            testMotor()
        case 2:
            testTc()
        case 3:
            testHeater()
        case 4:
            testDisplay()
        case 5:
            testMotor()
            time.sleep(1)
            testTc()
            time.sleep(1)
            testHeater()
            time.sleep(1)
            testDisplay()
            time.sleep(1)
        case _:
            print("invalid option")
