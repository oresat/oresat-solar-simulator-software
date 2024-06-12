# BBQ mode (to simulate a spinning satellite) NOW COLORIZED
# REQUIRES : Basilisk coarse sun sensor sim data as 'out.json'
# Import dependencies
from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
from time import sleep
import digitalio as dio
import pwmio
import board
import busio
import json
from lib import solar_simulator as ss

# Serial console logging settings
SERIAL_LOG  = False
PORT_SCAN = False

# Set the debug LED
led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT
led.value = True

# Create the simulator
sim = ss.SolarSimulator()
sim.uv_safe = True

# Calculate steps
steps = ss.calcSteps()

level = 0
intensity = 0
# wave = np.sin(np.linspace(0, np.pi, 360)) # bbq mode

# Reset any active lights
sim.setLEDs()
led.value = False

# Import basilisk data
with open('out.json', 'r') as jsonfile:
    bsk_dict = json.load(jsonfile)
    
bsk_data = np.array(bsk_dict['0'])

while True:
    # Calculate a 0-100 value from the wave
    intensity = int(bsk_data[level])

    print(intensity)
    # Gets LED brightness values at the appropriate level
    # From Charlene: Did some testing and calibration and looks like 80 is a magic number where
    # hal seemed to occupy most of the high spectrum, and blue was able to cover all of the bottom spectrum
    if intensity < 80:
        red = steps[0][0]
        grn = steps[1][(intensity//3)]
        blu = steps[2][(intensity//5)+2]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]
        #hal = steps[4][int(intensity/2.1)]
    if (intensity == 80 or intensity > 80):
        red = 0
        grn = steps[1][100]
        blu = steps[1][10]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]

    # Set LEDs and bulbs
    uv = 0 # Disable UV for safety
    sim.setLEDs(red,grn,blu,uv,hal)

    if SERIAL_LOG: print(f"Intensity: {intensity}, Level: {level}")

    # Increment and overflow the level every iteration
    level += 1
    if level > len(bsk_data)-1: level = 0
    sleep(0.1)
