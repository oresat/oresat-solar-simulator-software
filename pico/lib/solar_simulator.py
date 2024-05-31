# Solar Simulator hardware library
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep
import digitalio as dio
from pwmio import PWMOut
import board
from busio import I2C
from thermistor_helper import getTemp
import ulab.numpy as np

class SolarSimulator:
    MAX_VALUE = 65535
    def __init__(self):
        # Create I2C
        PORT_SCAN = True
        self.i2c = I2C(board.GP27, board.GP26)
        if PORT_SCAN:
            self.i2c.try_lock()
            found = self.i2c.scan()
            self.i2c.unlock()
            print(f"I2C initialized, addresses found: {[hex(i) for i in found]}")

        # Create ADS and MCP objects
        self.ads = ADS.ADS1015(self.i2c)
        self.mcp = MCP.MCP4728(self.i2c)

        # Create the Halogen object
        self.hal = PWMOut(board.GP28, frequency=50000, duty_cycle=0)
        
        # 	self.uv_safe = True
        #   self.therm_safe = True
	
    def setLEDs(self, a: int = 0, b: int = 0, c: int = 0, d: int = 0):
        self.mcp.channel_a.value = a
        self.mcp.channel_b.value = b
        self.mcp.channel_c.value = c
        #self.mcp.channel_d.value = d
    
    def setHalogen(self, duty_cycle: int):
        self.hal.duty_cycle = int(i*2*65535 / 100)

    # TODO: Return 3 lists (1 per channel) that contains bitshifted value, voltage as a float, and temperature as a float in Celsius
    # Could also return 1 list per data point rather than channel or return a single dictionary (with keys as "0", "1", and "2" or "ambient", "leds", and "cell")
    def checkThermals(self):
        for i in range(0,3):
            chan = AnalogIn(self.ads, i)
            print(f"Channel[{i}]: {chan.value>>4}, {chan.voltage}V, {self.calculateTemp(chan.voltage)}C")

    # Takes a thermistor's voltage and returns it's temperature in Celsius
    def calculateTemp(self, adc: float) -> float:
        rth = (10000) * (3.3 / adc) - 10000
        therm = 1 / ((np.log(rth/10000) / 3977) + (1/298.15))
        return therm - 273.15
