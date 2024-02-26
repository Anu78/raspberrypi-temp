import threading
import time
from drivers.motor import Stepper
from drivers.display import Display 
from drivers.thermocouple import Thermocouple

"""
joystick will be constantly polling.
display only moves when joystick moves 

websocket needs to be running and active at all time. same with database integrations. 
"""

def main(): 
    print("hello world.")

if __name__ == "__main__":
    main()
