# BBQ mode with thermal safety
# Import dependencies
from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep, monotonic_ns
from lib.thermistor_helper import getTemp
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
ads = ADS.ADS1015(i2c)
mcp = MCP.MCP4728(i2c) # Default address = 0x60
print("MCP4728 initialized, running safe BBQ mode")

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
    uv_steps  = np.linspace( uv_min,  uv_max, num=101, dtype=np.uint16)

    return [red_steps, grn_steps, blu_steps, uv_steps, pwm_steps]

# Calculate steps
steps = calcSteps(LIMITER)

# Sine wave vars
level = 0
intensity = 0
wave = np.sin(np.linspace(0, np.pi, 360))

# STATE MACHINE ITEMS
NS_OFFSET = monotonic_ns()
def getCurrentTime() -> int:
    return int((monotonic_ns()-NS_OFFSET)/1000000)

# Thermal check timing
therm_timer     = 0
THRM_CHECK      = 50
THRM_LEDS_SHTDN = 100 # In Celsius
THRM_HTSK_SHTDN = 60  # In Celsius
THRM_CELL_SHTDN = 80  # In Celsius
THRM_RSM        = 45  # In Celsius
lights_en       = True
lights_upd      = True

def checkThermals():
    channels = []
    for i in range(0,4):
        chan = AnalogIn(ads, i)
        value, voltage, temp_c = chan.value>>4, chan.voltage, getTemp(chan.voltage)
        channels.append([value, voltage, temp_c])
        #print(f"Channel[{i}]: {chan.value>>4}, {chan.voltage}V, {getTemp(chan.voltage)}C")
    return channels

# Reset any active lights
setLEDs()
led.value = False

while True:
    # Calculate a 0-100 value from the wave
    intensity = int(100*wave[level])

    # Gets LED brightness values at the appropriate level
    red = steps[0][intensity]
    grn = steps[1][intensity]
    blu = steps[2][intensity]
    uv  = 0# steps[3][intensity]
    hal = steps[4][int(intensity/2.1)]
    
    # Set LEDs and bulbs
    uv = 0 # Disable UV for safety
    
    c_time = getCurrentTime()
    if c_time - therm_timer > THRM_CHECK:
        #print()
        #print(f"Thermal readings:")
        channels = checkThermals()
        
        if (channels[0][2] > THRM_LEDS_SHTDN) \
        or (channels[1][2] > THRM_HTSK_SHTDN) \
        or (channels[2][2] > THRM_CELL_SHTDN):
            lights_en = False
            setLEDs()
        
        cold = True
        for i in range(len(channels)):
            if i > 1: continue
            
            temp_c = channels[i][2]
            cold = True if temp_c < THRM_RSM else False
            print(f"CH{i}: {temp_c:0.2f}C")
        
        if not lights_en and cold: lights_en = True
        therm_timer = getCurrentTime()
    
    if lights_en: setLEDs(red, grn, blu, uv, hal)

    if SERIAL_LOG: print(f"Intensity: {intensity}, Level: {level}")

    # Increment and overflow the level every iteration
    level += 1
    if level > len(wave)-1: level = 0
    sleep(0.01)
