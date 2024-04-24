# Basilisk emulator client code

from time import sleep, monotonic_ns
import pwmio
import board

# Use the built in LED
data = 0
led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=data)

while True:
    new_data = input().strip()
    if new_data is not None:
        try:
            data = int(new_data)
        except Exception as e:
            data = data
        
        if data > 100: data = 100
        if data <   0: data = 0
        print(f"RX: {data}, dt: {type(data)}")
        led.duty_cycle = int(655.35 * data)
    sleep(0.1)