# Thermal safety code test

# Import dependencies
from ulab import numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep, monotonic, monotonic_ns
import digitalio as dio
import supervisor
import pwmio
import board
import busio
from lib.thermistor_helper import getTemp

# Light step calculations
MAX_VALUE = 65535
PWM_FREQ  = 50000
LIMITER   = 1

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
mcp = MCP.MCP4728(i2c)
print("I2C devices initialized, running state machine")

def setLEDs(r: int = 0, g: int = 0, b: int = 0, u: int = 0, h: int = 0) -> None:
    delay = 0.05
    # Set the value of the R, G, B, UV, and Halogen lights (docs coming soon :tm:)
    if mcp.channel_a.value != r:
        mcp.channel_a.value = r
        sleep(delay)
    if mcp.channel_b.value != g:
        mcp.channel_b.value = g
        sleep(delay)
    if mcp.channel_c.value != b:
        mcp.channel_c.value = b
        sleep(delay)
    #if mcp.channel_d.value != u:
    #    mcp.channel_d.value = u
    #    sleep(delay)
    if halogen.duty_cycle  != h:
        halogen.duty_cycle  = h
        sleep(delay)

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

# Reset any active lights
setLEDs()
led.value = False

# Set the LEDs and bulb
r = steps[0][-5]
g = steps[1][-5]
b = steps[2][-5]
h = steps[4][0]

setLEDs(r, g, b, 0, h)
#setLEDs(steps[0][10], steps[0][10], steps[0][10], 0, steps[0][10])

# TODO: Move to `lib/thermistor_helper.py`
def checkThermals():
    channels = []
    for i in range(0,4):
        chan = AnalogIn(ads, i)
        value, voltage, temp_c = chan.value>>4, chan.voltage, getTemp(chan.voltage)
        channels.append([value, voltage, temp_c])
        #print(f"Channel[{i}]: {chan.value>>4}, {chan.voltage}V, {getTemp(chan.voltage)}C")
    return channels


# STATE MACHINE ITEMS
NS_OFFSET = monotonic_ns()
def getCurrentTime() -> int:
    return int((monotonic_ns()-NS_OFFSET)/1000000)

therm_timer = 0
THRM_CHECK  = 500
THRM_SHTDN  = 45
THRM_RSM    = 40
lights_en = False
light_stat = lights_en
led_timer   = 0
LED_TGL     = 150
led_value   = False

while True:
    c_time = getCurrentTime()
    if c_time - therm_timer > THRM_CHECK:
        print()
        print(f"Thermal readings:")
        channels = checkThermals()
        for i in range(len(channels)):
            if i > 0: continue

            temp_c = channels[i][2]
            print(temp_c)

            if temp_c > THRM_SHTDN:
                lights_en = False
                setLEDs()
            elif temp_c <= THRM_RSM:
                lights_en = True

        if lights_en != light_stat: setLEDs(r, g, b, 0, h)
        light_stat = lights_en
        therm_timer = getCurrentTime()

    if c_time - led_timer > LED_TGL:
        led_value = not led_value
        led.value = led_value
        led_timer = getCurrentTime()

    #print(c_time)
    sleep(0.01)
