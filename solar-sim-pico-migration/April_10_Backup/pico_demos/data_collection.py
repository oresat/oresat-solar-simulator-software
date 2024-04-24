# MANUAL DATA COLLECTION CODE

from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep, monotonic_ns
import digitalio as dio
import pwmio
import board
import busio

SERIAL_LOG  = True
SERIAL_PLOT = False
PORT_SCAN = False
PWM_FREQ = 50000


MAX_VALUE = 65535
system_state = 1 # what is system_state??? also from sample code
limiter = 1

# Set the PWM pinout
halogen = pwmio.PWMOut(board.GP28, frequency=PWM_FREQ, duty_cycle=0, variable_frequency=False)

# Init I2C and scan for ports
i2c = busio.I2C(board.GP27, board.GP26)
if PORT_SCAN:
    i2c.try_lock()
    found = i2c.scan()
    i2c.unlock()
    print(f"I2C initialized, addresses found: {[hex(i) for i in found]}")

# Init I2C devices
ads = ADS.ADS1015(i2c) # Default address = 0x48
mcp = MCP.MCP4728(i2c) # Default address = 0x60
print("Devices initialized, running data collection")

def setLEDs(r: int = 0, g: int = 0, b: int = 0, u: int = 0, h: int = 0):
    # Set the value of the R, G, B, UV, and Halogen lights (docs coming soon :tm:)
    mcp.channel_a.value = r
    mcp.channel_b.value = g
    mcp.channel_c.value = b
    mcp.channel_d.value = u
    halogen.duty_cycle  = h

def calc_steps(limiter: float):
    # Calculate the interpolation steps from a set intensity limiter (docs coming soon :tm:)
    # max_voltage = int(65535 * limiter)
    red_min = 10756
    grn_min = 10140
    blu_min = 10620
    UV_min  = 10620
    PWM_min = 0
    red_max = int(MAX_VALUE * limiter)
    grn_max = int(MAX_VALUE * limiter)
    blu_max = int(MAX_VALUE * limiter)
    UV_max  = int(MAX_VALUE * limiter)
    PWM_max = int(limiter * 65535 * .5) # KEEP .5 MULTIPLIER UNTIL BETTER POWER SUPPLY IS USED; DRAWS TOO MUCH POWER OTHERWISE

    # Calculate steps between minimum and maximum values
    red_steps = np.linspace(red_min, red_max, num=101, dtype=np.uint16)
    grn_steps = np.linspace(grn_min, grn_max, num=101, dtype=np.uint16)
    blu_steps = np.linspace(blu_min, blu_max, num=101, dtype=np.uint16)
    PWM_steps = np.linspace(PWM_min, PWM_max, num=101, dtype=np.uint16)

    if system_state == 2:
        UV_steps = [0] * 101
    else:
        UV_steps = np.linspace(UV_min, UV_max, num=101, dtype=np.uint16)

    return [red_steps, grn_steps, blu_steps, UV_steps, PWM_steps]

# Calculates 'steps' and sweeps through the intensity 'level'
# by 5 everytime and switches sweep direction at 0 and 100
steps = calc_steps(limiter)


command_prompt = """Select a channel: [red, grn, blu, uv, hal]
Give a value: 0-100%
Multiple channels can be set by using comma separation
Example inputs: (g:50), (r:100, b:32, uv:0), etc."""

# Valid string inputs from the terminal
valid_inputs = [ 'r', 'red', 'g', 'grn', 'green', 'b', 'blu', 'blue', 'u', 'uv', 'h', 'hal', 'halogen' ]

# LED channel value buffer
led_buf = {
    'r': 0,
    'g': 0,
    'b': 0,
    'u': 0,
    'h': 0,
}

# Reset any active lights
setLEDs()

while True:
    print(f"======= Current values - R={led_buf['r']}, G={led_buf['g']}, B={led_buf['b']}, UV={led_buf['u']}, H={led_buf['h']} =======\n")
    print(command_prompt)
    print('-' * 60)

    # Get the data from the serial connection
    data = input("Enter a command: ", )

    # Format input string
    data = data.replace(' ', '').lower().split(',')
    # print(data)

    # Get data from each input
    for item in data:
        item = item.split(':')
        if len(item) > 1:
            item[1] = int(item[1])
            # print(f"Split item found: {item}")

            if item[0] in valid_inputs and item[1] <= 100 and item[1] >= 0:
                led_buf[item[0][0]] = item[1]

    print()
    if 'reset' in data or 'clear' in data:
        led_buf['r'] = 0
        led_buf['g'] = 0
        led_buf['b'] = 0
        led_buf['u'] = 0
        led_buf['h'] = 0

    calc_start = monotonic_ns()
    #steps = calc_steps(limiter) # 1ms slower lol

    # Gets LED brightness values at the appropriate level
    red = steps[0][led_buf['r']]
    grn = steps[1][led_buf['g']]
    blu = steps[2][led_buf['b']]
    uv  = steps[3][led_buf['u']]
    hal = steps[4][led_buf['h']]

    uv = 0 # Disable UV for safety

    calc_end = monotonic_ns()
    sleep(0.1)

    if SERIAL_LOG:
        print(f"red:{red},grn:{grn},blu:{blu},uv:{uv},hal:{hal},lim:{limiter},calc_time:{(calc_end-calc_start)/1000:0.3f}us")
    # if SERIAL_PLOT:
    #     print(f"({red}, {grn}, {blu}, {uv}, {hal}, {limiter}, {level})")

    # Set the LEDs and bulb
    setLEDs(red,grn,blu,uv,hal)
