##### MVP/PRIORITY #####
# Create TK application
# Add a button to connect to hard coded serial port
# Add a button to start and stop sending serial data
# Add a text/number box that takes in a value to send to the


##### Concept #####
# Choose a port to connect to serial over (as well as port settings)
# Choose an output format (ie. raw serial values, debug version that is currently running on the Pico now, Basilisk outputs, etc.)
# Set the sun's intensity with a slider or in/decrement a value
# Send test data and receive telemetry data from Pico (ie. thermals, individual light channel's intensity, etc.)


##### Nice to Haves #####
# Change the virtual environment to use the dedicated `oresat` anaconda environment (when created later)
# Create a requirements.txt (probably just pyserial tbh, maybe pyinstaller or something for packaging, but probably not necessary)

import tkinter as tk
import serial as s
import time

DEVICE_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

# serial = s.Serial(port=DEVICE_PORT, baudrate=BAUDRATE)
# serial.open()
with s.Serial(DEVICE_PORT, BAUDRATE, timeout=1) as serial:
    serial.write(b'Beginning transfers\r')
    while True:
        serial.write(b'Hello from pyserial!\r')
        serial.readline()
        data = serial.readline().strip()
        if data: print(f"Pico: {''.join([chr(char) for char in data])}")
        time.sleep(0.1)
