import asyncio
from bleak import BleakClient
import threading

class BLEReader:
    def __init__(self, address, char_uuid, data_changed_callback=None):
        self.device_address = address
        self.characteristic_uuid = char_uuid
        self.data_changed_callback = data_changed_callback
        self.loop = asyncio.new_event_loop()
        self.client = BleakClient(self.device_address, loop=self.loop)
        self.running = False  # Flag to control the loop
        self.thread = None  # Initialize thread attribute

    def handle_notification(self, sender, data):
        combined_data = data[0]
        direction = combined_data & 0x07
        switch_state = (combined_data >> 3) & 0x01
        new_data = (direction, switch_state)
        if self.data_changed_callback:
            self.data_changed_callback(new_data)

    async def maintain_connection(self):
        self.running = True
        try:
            await self.client.connect()
            await self.client.start_notify(self.characteristic_uuid, self.handle_notification)
            while self.running:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if self.client and self.client.is_connected:
                await self.client.stop_notify(self.characteristic_uuid)
                await self.client.disconnect()

    def start(self):
        # Define and start the thread, and assign it to self.thread
        self.thread = threading.Thread(target=self.loop.run_until_complete, args=(self.maintain_connection(),), daemon=True)
        self.thread.start()

    def stop(self):
        # Set the running flag to False to stop the loop
        self.running = False

        # Define a new coroutine for stopping notifications and disconnecting
        async def stop_and_disconnect():
            if self.client and self.client.is_connected:
                # Stop notifications and wait until it's done
                await self.client.stop_notify(self.characteristic_uuid)
                # Disconnect the client and wait until it's done
                await self.client.disconnect()

        # Stopping the asyncio event loop and executing cleanup
        if self.loop and not self.loop.is_closed():
            # Schedule the stop_and_disconnect coroutine to run and wait for it to complete
            disconnect_task = asyncio.run_coroutine_threadsafe(stop_and_disconnect(), self.loop)
            # Wait for the disconnection task to finish
            disconnect_task.result()

            # Stop the event loop after all disconnection and cleanup tasks have completed
            self.loop.call_soon_threadsafe(self.loop.stop)

        # Wait for the thread to finish if it was started
        if self.thread is not None:
            self.thread.join()
