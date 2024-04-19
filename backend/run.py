#!env/bin/python3
import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem
from drivers.thermocouples import MultiThermocouple
from drivers.keyboard import Keyboard
from communications.logging import Logger
from drivers.heater import Heater

def moveMotor():
  stepper.move(3200)
def getLeftTemp():
  t = multi.get_temperature_str(0)
  print(t)
  return multi.get_temperature_str(0)
def getRightTemp():
  t = multi.get_temperature_str(1)
  print(t)
  return multi.get_temperature_str(1)
def preheat_heater():
  heater.preheat()
def stop_heater():
  heater.off()

def buildMenu():
    rootMenu = MenuItem("main menu")
    motorControl = MenuItem("motor control")

    motorControl + MenuItem("move apart", action=moveMotor)
    motorControl + MenuItem("move in")
    motorControl + MenuItem("home")
    calibrate = MenuItem("calibrate")
    calibrate + MenuItem("move in") 
    calibrate + MenuItem("move out")
    calibrate + MenuItem("cur steps:", update=None)
    calibrate + MenuItem("set compressed", action=None)

    motorControl + calibrate 

    preheat = MenuItem("preheat")
    preheat + MenuItem("lplate:", update=getLeftTemp)
    preheat + MenuItem("rplate:", update=getRightTemp)
    preheat + MenuItem("start preheating", action=preheat_heater)
    preheat + MenuItem("stop preheating", action=stop_heater)

    about = MenuItem("about")
    about + MenuItem("sd 2023-24")
    about + MenuItem("code: git - anu78/sd23-24")
    about + MenuItem("play a game")

    connection = MenuItem("connection")
    connection + MenuItem("ip: ", once=None)
    connection + MenuItem("online?")

    rootMenu + motorControl
    rootMenu + preheat
    rootMenu + about
    rootMenu + connection

    return rootMenu

def cleanup():
    print("\n interrupted by user. cleaning up")
    multi.cleanup()
    stepper.cleanup()
    lcd.cleanup(clear=True)
    heater.cleanup()
    print("safely exiting...")
    exit(0)

# globals
logger = Logger()
logger.setup_logging()
lcd = Display(20, 4, 0x27, buildMenu())
multi = MultiThermocouple(5, 6, 13, 8)
stepper = Stepper(pul=19, dir=26, stepsPerRevolution=3200, limit_switch_pin=10)
heater = Heater(16, 20, multi, 0, 1)
keyboard = Keyboard()

def loop():
    try:
      for press in keyboard:
        if press == "u":
          lcd.move(-1)
        elif press == "d":
          lcd.move(1)
        elif press == "l":
          lcd.outNav()
        elif press == "r":
          lcd.intoNav()
        elif press == "sel":
          lcd.select()
    except KeyboardInterrupt:
          print("\ninterrupted by user. cleaning up...")
          cleanup()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cleanup()


if __name__ == "__main__":
    print("program started")
    loop()
