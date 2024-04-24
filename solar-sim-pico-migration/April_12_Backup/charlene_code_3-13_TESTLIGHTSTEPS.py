# Write your code here :-)
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio as dio
import pwmio
from time import sleep
import board
import busio

global system_state = 1
global BB_PER = 4000 # what is BB_PER ??? it was from sample code
global limiter = 0.3
global level = 100

# Set the PWM pinout
halogen = pwmio.PWMOut(board.GP28, frequency=5000, duty_cycle=0)

# Init I2C and scan for ports
i2c = busio.I2C(board.GP27, board.GP26)
i2c.try_lock()
found = i2c.scan()
i2c.unlock()
print(f"I2C initialized, addresses found: {[hex(i) for i in found]}")

# Init I2C devices
ads0 = ADS.ADS1015(i2c, address=0x48) # Default address = 0x48
#ads1 = ADS.ADS1015(i2c, address=0x49) # Default address = 0x49, Output not connected?
mcp = MCP.MCP4728(i2c)
print("Devices initialized, running main loop")

MAX_VALUE = 65535
def setLEDs(a: int = 0, b: int = 0, c: int = 0, d: int = 0):
    mcp.channel_a.value = a
    mcp.channel_b.value = b
    mcp.channel_c.value = c
    mcp.channel_d.value = d

def calc_steps(limiter):
    '''
    Calculates the light steps for the LEDs based on calibrated
    mins/max and any specified limiter

    params limiter: float between 0-1 to scale the power for safety
    '''
    max_voltage = int(65535 * limiter)
    red_start = 10756
    grn_start = 10140
    blu_start = 10620
    UV_start  = 10620
    PWM_start = 0 * BB_PER / 100
    red_max = int(65535 * limiter)
    grn_max = int(65535 * limiter)
    blu_max = int(65535 * limiter)
    UV_max  = int(65535 * limiter)
    PWM_max = int(75 * limiter * BB_PER / 100)
    red_steps = linspace(red_start, red_max, num=101, dtype=uint16)
    grn_steps = linspace(grn_start, grn_max, num=101, dtype=uint16)
    blu_steps = linspace(blu_start, blu_max, num=101, dtype=uint16)
    PWM_steps = linspace(PWM_start, PWM_max, num=101, dtype=uint16)
    if system_state == 2:
        UV_steps = [0] * 101
    else:
        UV_steps = linspace(UV_start, UV_max, num=101, dtype=uint16)
    return [red_steps, grn_steps, blu_steps, UV_steps, PWM_steps]

calc_steps(limiter)
a = steps[0][level]
b = steps[1][level]
c = steps[2][level]
d = steps[3][level]

while True:
    # Read all ADC channels
    for i in range(0,4):
        chan = AnalogIn(ads0, i)
        print(f"Channel[{i}]: {chan.value}, {chan.voltage}V")
    print('-'*40)
    sleep(1)

    print("Setting HALOGEN")
    setLEDs()

    #for i in range(100):
        # PWM LED up and down
    #    if i < 50:
    #       halogen.duty_cycle = int(i * 2 * 65535 / 100)  # Up
    #    else:
    #        halogen.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
    #    sleep(0.01)
    # halogen.duty_cycle = 0
    # sleep(1)

