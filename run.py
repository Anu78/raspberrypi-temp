import threading
import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem 
from drivers.thermocouple import Thermocouple
import websockets

"""
joystick will be constantly polling.
display only moves when joystick moves 

websocket needs to be running and active at all time. same with database integrations. 
"""
def moveMotor(): 
    print("move motor ran")
    stepper.move(3200)
def getIPAddress():
    from subprocess import check_output

    ips = check_output(["hostname", "--all-ip-addresses"])

    parsed = ips.decode("utf-8").strip()

    # sometimes this includes the mac address, so filtering:
    return parsed[parsed.find(" ") :]

def getThermocoupleTemp(): 
    return tc.get()

def buildMenu(): 
    rootMenu = MenuItem("main menu")
    motorControl = MenuItem("motor control")
    motorCalibrate = MenuItem("calibrate")
    motorCalibrate.addChildren([MenuItem("menu test")])

    motorControl.addChildren([MenuItem("motor out", action=moveMotor), MenuItem("motor in"), MenuItem("motor home"), motorCalibrate])

    preheat = MenuItem("preheat")
    preheat.addChildren([
        MenuItem("temp 1:", update=getThermocoupleTemp)
        ])

    about = MenuItem("about")
    about.addChildren([
        MenuItem("sd 2023-24"), MenuItem("code:"), MenuItem("todo")
        ])

    connection = MenuItem("connection")
    connection.addChildren([MenuItem("ip: ", once=getIPAddress), MenuItem("online?")])

    rootMenu.addChildren([motorControl, preheat, about, connection])

    return rootMenu

# globals
lcd = Display(20, 4, 0x27, buildMenu())
tc = Thermocouple("main",chipSelect=23, clock=11, data=9)
stepper = Stepper(pul=17, dir=27, stepsPerRevolution=3200)

def fancyInterpreter():
    """
    this is a substitute method for the joystick
    """
    try:
        while True:
            s = input(">> ")

            if s == "u":
                lcd.move(-1)
            elif s == "h":
                print("h for help | u d l r to m | sel to select | back for back")
            elif s == "d":
                lcd.move(1)
            elif s == "l":
                lcd.outNav()
            elif s == "r":
                lcd.intoNav()
            elif s == "sel":
                lcd.select()
            elif s == "back":
                lcd.back()
            else:
                print("command not recognized")
    except KeyboardInterrupt:
        print("\n interrupted by user. cleaning up")
        tc.cleanup()
        stepper.cleanup()
        lcd.cleanup(clear=False)
        exit()

def main(): 
    print("started.")
    fancyInterpreter()

if __name__ == "__main__":
    main()
