#!/usr/bin/env python3
"""Module to control a Linak Desk over Bluetooth"""
import struct
import threading
from time import time
from bluepy.btle import Peripheral, DefaultDelegate

class Desk:
    """Control a Linak Bluetooth desk"""
    SERVICE_INFO = '99FA0021-338A-1024-8A49-009C0215F78A'
    SERVICE_CONTROL = '99fa0002-338a-1024-8a49-009c0215f78a'
    SERVICE_MOVE_TO = '99FA0031-338A-1024-8A49-009C0215F78A'

    class NotificationReader(DefaultDelegate):
        """Wait for notifications in a separate thread and process them"""
        def __init__(self, _per, _callback):
            DefaultDelegate.__init__(self)
            self.per = _per
            self.callback = _callback
            self.running = True
            self.thread = None
            self.per.withDelegate(self)

        def work(self):
            """Start the worker thread"""
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

        def stop(self):
            """Stop the worker thread"""
            self.running = False
            if self.thread is not None:
                self.thread.join()
                self.thread = None

        def _run(self):
            """The main function inside the thread, wait for notifications"""
            while self.running:
                self.per.waitForNotifications(1.0)

        def handleNotification(self, cHandle, data):
            """Call the user callback for the notifcation"""
            self.callback(data)

    def __init__(self, mac, print_info=False):
        self.per = Peripheral(mac, "random")
        self.print_info = print_info
        self.height = 0
        self.speed = 0
        self.notification_worker = self.NotificationReader(self.per, self.update_information)
        self.last_change = time()

    def oneshot(self, position):
        """Set the table to the given position and disconnect"""
        try:
            self.listen()
            self.move_to_position(position)
        finally:
            self.stop()
        return self.height

    def oneshot_read_info(self):
        """Read the current information about the desk and disconnect"""
        try:
            self.update_information(self._read(self.SERVICE_INFO))
        finally:
            self.stop()
        return self.height

    def listen(self):
        """Subscribe to changes and start a worker thread to process them"""
        self.notification_worker.work()
        self.subscribe()

    def stop(self):
        """Disconnect from the desk"""
        self.notification_worker.stop()
        self.per.disconnect()

    def subscribe(self):
        """Subscribe to notifications of changes"""
        handle = self._get_handle(self.SERVICE_INFO)
        self.per.writeCharacteristic(handle + 1, self._command(1), withResponse=False)
        self.update_information(self._read(self.SERVICE_INFO, handle=handle))

    def move_to_position(self, position):
        """Move the desk to a given position"""
        self._wake_up()
        handle = self._get_handle(self.SERVICE_MOVE_TO)
        while position != self.height and not self._did_timeout():
            self._write(self.SERVICE_MOVE_TO, position, handle=handle)

    def update_information(self, data):
        """Update the main information about the desk based on the raw data received"""
        self._update_height(data)
        self._update_speed(data)
        self.last_change = time()
        self.print()

    def _update_height(self, data):
        """Update the height of the desk from raw data"""
        self.height = struct.unpack('<H', data[0:2])[0]

    def _update_speed(self, data):
        """Update the speed of the desk from raw data"""
        self.speed = struct.unpack('H', data[2:4])[0] & 0xFFF

    @staticmethod
    def _command(data):
        """Pack a given command to bytes for transmission"""
        return struct.pack('<H', data)

    def _get_handle(self, uuid):
        """Get the handle for a characteristic based on its UUID"""
        return self.per.getCharacteristics(uuid=uuid)[0].getHandle()

    def _write(self, service, command, handle=None):
        """Write a characteristic"""
        if handle is None:
            handle = self._get_handle(service)
        return self.per.writeCharacteristic(handle, self._command(command), withResponse=False)

    def _read(self, service, handle=None):
        """Read a characteristic"""
        if handle is None:
            handle = self._get_handle(service)
        return self.per.readCharacteristic(handle)

    def _move_up(self):
        """Move the desk up one step"""
        self._write(self.SERVICE_CONTROL, 71)

    def _move_down(self):
        """Move the desk down one step"""
        self._write(self.SERVICE_CONTROL, 70)

    def _wake_up(self):
        """Send the wakeup command"""
        self._write(self.SERVICE_CONTROL, 254)

    def _did_timeout(self):
        """Check if a timeout has occured since the last change"""
        if time() - self.last_change > 3.0:
            return True
        return False

    def print(self):
        """Print information about the desk on the console"""
        if self.print_info:
            print("Height: " + str(self.height) + ", speed: " + str(self.speed))


if __name__ == "__main__":
    # Parse arguments
    import argparse
    PARSER = argparse.ArgumentParser(description='Move a bluetooth Linak desk to a given position')
    PARSER.add_argument(
        'mac', metavar='MAC', type=str,
        help='The bluetooth MAC address of the desk',
    )
    PARSER.add_argument(
        'position', metavar='POSITION', type=int,
        help='The target position of the desk'
    )
    PARSER.add_argument(
        '-q', '--quiet', action='store_false',
        help="Quiet mode, do not print information"
    )
    ARGS = PARSER.parse_args()

    # Connect to the desk and execute the command
    Desk(ARGS.mac, print_info=ARGS.quiet).oneshot(ARGS.position)
