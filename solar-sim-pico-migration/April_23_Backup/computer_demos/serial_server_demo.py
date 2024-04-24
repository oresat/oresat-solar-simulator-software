# Host computer serial server demo code

# MUST INSTALL `pyserial` BEFORE RUNNING
# May also need to change `device_port` depending on what the Pico shows up as

import serial as s
import time

DEVICE_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# serial = s.Serial(port=DEVICE_PORT, baudrate=BAUDRATE)
# serial.open()
with s.Serial(DEVICE_PORT, BAUDRATE, timeout=1) as serial:
    serial.write(b'Beginning transfers\r')
    while True:
        serial.write(b'Hello from pyserial!\r'); serial.readline()
        data = serial.readline().strip()
        if data:
            print(f"Pico: {''.join([chr(char) for char in data])}")
        time.sleep(0.1)