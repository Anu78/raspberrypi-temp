#!env/bin/python3
import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem, ToggleItem
from drivers.thermocouples import readTc 
from drivers.keyboard import Keyboard
from communications.logging import Logger
from drivers.heater import Heater

def moveOut():
  stepper.move(100)
def moveIn():
  stepper.move(-100)
def compress():
  stepper.compress()
heater = Heater(17, 16, readTc) # 17 is left.  
def heater_on():
  heater.on()
def heater_off():
  heater.off()
def buildMenu():
    rootMenu = MenuItem("main menu")
    motorControl = MenuItem("motor control")

    motorControl + MenuItem("move apart", action=moveIn)
    motorControl + MenuItem("move in", action=moveOut)
    motorControl + MenuItem("home")
    calibrate = MenuItem("calibrate")
    calibrate + MenuItem("move in") 
    calibrate + MenuItem("move out")
    calibrate + MenuItem("cur steps:", update=None)
    calibrate + MenuItem("set compressed", action=None)
    motorControl + calibrate 

    preheat = MenuItem("heating")
    preheat + MenuItem("lplate:", update=lambda : readTc(0))
    preheat + MenuItem("rplate:", update=lambda : readTc(1))
    preheat + MenuItem("bag:", update=lambda : readTc(7))
    preheat + ToggleItem("prepare: ", on_action=heater_on, off_action=heater_off)

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
    stepper.cleanup()
    lcd.cleanup(clear=True)
    heater.cleanup()
    print("safely exiting...")
    exit(0)

# globals
logger = Logger()
logger.setup_logging()
lcd = Display(20, 4, 0x27, buildMenu())
stepper = Stepper(pul=19, dir=27, stepsPerRevolution=3200, limit_switch_pin=10)
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
