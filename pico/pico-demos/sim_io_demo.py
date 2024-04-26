# Read from thermistors and photodiode and write to LEDs and halogen bulb

import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio as dio
import pwmio
from time import sleep
import board
import busio
from lib.thermistor_helper import getTemp

# Set the PWM pinout
halogen = pwmio.PWMOut(board.GP28, frequency=50000, duty_cycle=0)

# Init I2C and scan for ports
i2c = busio.I2C(board.GP27, board.GP26)
i2c.try_lock()
found = i2c.scan()
i2c.unlock()
print(f"I2C initialized, addresses found: {[hex(i) for i in found]}")

# Init I2C devices
ads = ADS.ADS1015(i2c) # Default address = 0x48
mcp = MCP.MCP4728(i2c)
print("Devices initialized, running main loop")

MAX_VALUE = 65535
def setLEDs(a: int = 0, b: int = 0, c: int = 0, d: int = 0):
    mcp.channel_a.value = a
    mcp.channel_b.value = b
    mcp.channel_c.value = c
    mcp.channel_d.value = d

while True:
    # Read all ADC channels
    print('-'*40)
    for i in range(0,4):
        chan = AnalogIn(ads, i)
        print(f"Channel[{i}]: {chan.value>>4}, {chan.voltage}V, {getTemp(chan.voltage)}C")
    print('-'*40)
    sleep(1)

    print("Setting HALOGEN")
    setLEDs()
    for i in range(100):
        if i < 50:
            halogen.duty_cycle = int(i * 2 * 65535 / 100)  # Up
        else:
            halogen.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
        sleep(0.01)
    halogen.duty_cycle = 0
    #sleep(1)

    print("Setting RED")
    setLEDs(a=MAX_VALUE)
    sleep(1)

    print("Setting GREEN")
    setLEDs(b=MAX_VALUE)
    sleep(1)

    print("Setting BLUE")
    setLEDs(c=MAX_VALUE)
    sleep(1)

    #print()
