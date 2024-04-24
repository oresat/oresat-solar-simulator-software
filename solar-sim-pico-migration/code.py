# CircuitPython code for Pico

from time import sleep, monotonic_ns
import digitalio as dio
import board
import busio
import supervisor

while True:
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        if value == "": continue
        print(f"RX: {value}")
    sleep(0.1)