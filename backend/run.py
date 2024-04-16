#!env/bin/python3
import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem
from drivers.thermocouple import Thermocouple
from drivers.joystick import JoystickReader
from communications.logging import Logger


def moveMotor():
    stepper.move(3200)
def getLeftTemp():
    return tcLeft.get()
def getRightTemp():
    return tcRight.get()

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
    preheat + MenuItem("start preheating")
    preheat + MenuItem("stop preheating")

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
    tcLeft.cleanup()
    tcRight.cleanup()
    stepper.cleanup()
    lcd.cleanup(clear=False)
    print("safely exiting...")
    exit(0)


# globals
logger = Logger()
logger.setup_logging()
lcd = Display(20, 4, 0x27, buildMenu())
tcLeft = Thermocouple("left plate", chipSelect=7, clock=11, data=9)
tcRight = Thermocouple("right plate", chipSelect=8, clock=11, data=9)
stepper = Stepper(pul=19, dir=26, stepsPerRevolution=3200)
joystick = JoystickReader(switch_pin=18)


def moveUp():
    lcd.move(-1)


def moveDown():
    lcd.move(1)


def moveLeft():
    lcd.outNav()


def moveRight():
    lcd.intoNav()


def click():
    lcd.select()


joystick.assignAction("up", moveUp)
joystick.assignAction("down", moveDown)
joystick.assignAction("left", moveLeft)
joystick.assignAction("right", moveRight)
joystick.assignAction("click", click)


def loop():
    try:
        joystick.read()
    except KeyboardInterrupt:
        print("\ninterrupted by user. cleaning up...")
        cleanup()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cleanup()


if __name__ == "__main__":
    print("program started")
    loop()