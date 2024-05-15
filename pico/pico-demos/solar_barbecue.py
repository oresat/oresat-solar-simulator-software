# BBQ mode (to simulate a spinning satellite) NOW COLORIZED
# Import dependencies
from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
from time import sleep
import digitalio as dio
import pwmio
import board
import busio

# Serial console logging settings
SERIAL_LOG  = False
PORT_SCAN = False

# Light step calculations
MAX_VALUE = 65535
PWM_FREQ = 50000
LIMITER = 1

# Set the debug LED
led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT
led.value = True

# Set the PWM pinout
halogen = pwmio.PWMOut(board.GP28, frequency=PWM_FREQ, duty_cycle=0)

# Init I2C and scan for ports
i2c = busio.I2C(board.GP27, board.GP26)

# Init I2C devices
mcp = MCP.MCP4728(i2c) # Default address = 0x60
print("MCP4728 initialized, running sine dimming")

def setLEDs(r: int = 0, g: int = 0, b: int = 0, u: int = 0, h: int = 0) -> None:
    # Set the value of the R, G, B, UV, and Halogen lights (docs coming soon :tm:)
    mcp.channel_a.value = r
    mcp.channel_b.value = g
    mcp.channel_c.value = b
    mcp.channel_d.value = u
    halogen.duty_cycle  = h

def calcSteps(LIMITER: float) -> list:
    # Calculate the interpolation steps from a set intensity limiter (docs coming soon :tm:)
    red_min = 10756
    grn_min = 10140
    blu_min = 10620
    uv_min  = 10620
    pwm_min = 0
    red_max = int(MAX_VALUE * LIMITER)
    grn_max = int(MAX_VALUE * LIMITER)
    blu_max = int(MAX_VALUE * LIMITER)
    uv_max  = int(MAX_VALUE * LIMITER)
    pwm_max = int(LIMITER * MAX_VALUE * .5) # KEEP .5 MULTIPLIER UNTIL BETTER POWER SUPPLY IS USED; DRAWS TOO MUCH POWER OTHERWISE

    # Calculate steps between minimum and maximum values
    red_steps = np.linspace(red_min, red_max, num=101, dtype=np.uint16)
    grn_steps = np.linspace(grn_min, grn_max, num=101, dtype=np.uint16)
    blu_steps = np.linspace(blu_min, blu_max, num=101, dtype=np.uint16)
    pwm_steps = np.linspace(pwm_min, pwm_max, num=101, dtype=np.uint16)
    uv_steps  = (np.linspace(uv_min, uv_max, num=101, dtype=np.uint16))
    
    return [red_steps, grn_steps, blu_steps, uv_steps, pwm_steps]

# Calculate steps
steps = calcSteps(LIMITER)

level = 0
intensity = 0
wave = np.sin(np.linspace(0, np.pi, 360))

# Reset any active lights
setLEDs()
led.value = False

while True:
    # Calculate a 0-100 value from the wave
    intensity = int(100*wave[level])

    print(intensity)
    # Gets LED brightness values at the appropriate level
    # From Charlene: Did some testing and calibration and looks like 80 is a magic number where
    # hal seemed to occupy most of the high spectrum, and blue was able to cover all of the bottom spectrum
    if intensity < 80:
        red = steps[0][0]
        grn = steps[1][0]
        blu = steps[2][0]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]
        #hal = steps[4][int(intensity/2.1)]
    if (intensity == 80 or intensity > 80):
        red = 0
        grn = 0
        blu = steps[2][100]
        uv  = steps[3][intensity]
        hal = steps[4][int(intensity)]

    # Set LEDs and bulbs
    uv = 0 # Disable UV for safety
    setLEDs(red,grn,blu,uv,hal)

    if SERIAL_LOG: print(f"Intensity: {intensity}, Level: {level}")

    # Increment and overflow the level every iteration
    level += 1
    if level > len(wave)-1: level = 0
    sleep(0.1)
