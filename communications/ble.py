import asyncio
from bleak import BleakClient
import struct

class BLEJoystickReader:
    def __init__(self, address, char_uuid_x, char_uuid_y, deadzone=5):
        self.device_address = address
        self.characteristic_uuid_x = char_uuid_x
        self.characteristic_uuid_y = char_uuid_y
        self.joystickX = 50 
        self.joystickY = 50
        self.deadzone = deadzone 

    async def read_data(self):
        async with BleakClient(self.device_address) as client:
            if client.is_connected:
                print(f"Connected to {self.device_address}")

                while client.is_connected:
                    # Read X and Y values
                    data_x, data_y = None, None
                    if client.services.get_characteristic(self.characteristic_uuid_x):
                        data_x = await client.read_gatt_char(self.characteristic_uuid_x)
                        data_x = struct.unpack("<I", data_x)[0]  # Assuming data format is unsigned int

                    if client.services.get_characteristic(self.characteristic_uuid_y):
                        data_y = await client.read_gatt_char(self.characteristic_uuid_y)
                        data_y = struct.unpack("<I", data_y)[0]  # Assuming data format is unsigned int

                    # Interpret directions based on joystick values
                    if data_x is not None and data_y is not None:
                        x_center = 50  # Adjust this value if necessary
                        y_center = 50  # Adjust this value if necessary
                        direction = ""

                        if data_x < x_center - self.deadzone:  # Consider a deadzone to avoid drift
                            direction = "Left"
                        elif data_x > x_center + self.deadzone:
                            direction = "Right"

                        if data_y < y_center - self.deadzone:
                            direction = "Down"
                        elif data_y > y_center + self.deadzone:
                            direction = "Up"

                        print(f"Joystick Direction: {direction if direction else 'Center'}")

                    await asyncio.sleep(0.1)  # Adjust polling rate as needed


    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.read_data())
    
    

# Usage
device_address = "EC:62:60:82:94:0E"
char_uuid_x = "00002a58-0000-1000-8000-00805f9b34fb"
char_uuid_y = "00002a59-0000-1000-8000-00805f9b34fb"
joystick_reader = BLEJoystickReader(device_address, char_uuid_x, char_uuid_y)
joystick_reader.start()
