# Pico serial client demo code

from time import sleep
import supervisor

while True:
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        if value == "": continue
        print(f"RX: {value}")
    sleep(0.1)
