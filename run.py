import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem 
from drivers.thermocouple import Thermocouple
from drivers.joystick import JoystickReader

def moveMotor(): 
    print("move motor ran")
    stepper.move(3200)

def getIPAddress():
    from subprocess import check_output

    ips = check_output(["hostname", "--all-ip-addresses"])

    parsed = ips.decode("utf-8").strip()

    return parsed[parsed.find(" ") :]

def getLeftTemp():
    return tcLeft.get()
def getRightTemp():
    return tcRight.get()
def buildMenu(): 
    rootMenu = MenuItem("main menu")
    motorControl = MenuItem("motor control")

    motorControl + MenuItem("motor out", action=moveMotor) 
    motorControl + MenuItem("motor in")
    motorControl + MenuItem("motor home")

    preheat = MenuItem("preheat")
    preheat + MenuItem("temp 1:", update=getLeftTemp)
    preheat + MenuItem("tenp 2:", update=getRightTemp)

    about = MenuItem("about")
    about + MenuItem("sd 2023-24")
    about + MenuItem("code:")
    about + MenuItem("todo")

    connection = MenuItem("connection")
    connection + MenuItem("ip: ", once=getIPAddress) 
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
lcd = Display(20, 4, 0x27, buildMenu())
tcLeft = Thermocouple("left plate",chipSelect=23, clock=11, data=9)
tcRight = Thermocouple("right plate",chipSelect=24, clock=11, data=9)
stepper = Stepper(pul=17, dir=27, stepsPerRevolution=3200)
joystick = JoystickReader(switch_pin=26)

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