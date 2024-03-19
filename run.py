#!/usr/bin/python3.11
import time
from drivers.stepper import Stepper
from drivers.display import Display, MenuItem 
from drivers.thermocouple import Thermocouple
import websockets

def moveMotor(): 
    print("move motor ran")
    stepper.move(3200)

def getIPAddress():
    from subprocess import check_output

    ips = check_output(["hostname", "--all-ip-addresses"])

    parsed = ips.decode("utf-8").strip()

    # sometimes this includes the mac address, so filtering:
    return parsed[parsed.find(" ") :]

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

def cleanup(): 
    print("\n interrupted by user. cleaning up")
    tc.cleanup()
    stepper.cleanup()
    lcd.cleanup(clear=False)
    bleReader.stop()
    print("safely exiting...")
    exit(0)

# globals
lcd = Display(20, 4, 0x27, buildMenu())
tc1 = Thermocouple("main",chipSelect=23, clock=11, data=9)
tc2 = Thermocouple("main",chipSelect=23, clock=11, data=9)
tc1_precise = Thermocouple("main",chipSelect=23, clock=11, data=9, model="max31856")
stepper = Stepper(pul=17, dir=27, stepsPerRevolution=3200)

async def loop():
    try:
        while True:
            if joystick[0] is None or joystick[1] == None:
                continue
            print(joystick)
            match joystick[0]: 
                case 1:
                    print("left")
                    lcd.outNav()
                case 2:
                    print("up")
                    lcd.move(-1)
                case 3:
                    print("right")
                    lcd.intoNav()
                case 4:
                    print("down")
                    lcd.move(1)
            if joystick[1] == 1:
                lcd.select()
            asyncio.sleep(2)
            
    except KeyboardInterrupt:
        print("\ninterrupted by user. cleaning up...")
        cleanup()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cleanup()

if __name__ == "__main__":
    print("program started")
    loop()
