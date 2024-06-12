# Solar Simulator hardware Python module
import ulab.numpy as np
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio as dio
from busio import I2C
from pwmio import PWMOut
import board

MAX_VALUE = 65535

class SolarSimulator:
    # Initializes the Solar Simulator module
    def __init__(self, pwm_freq: int = 50000, verbose: int = 0):
        # Initialize constants
        if verbose: print("Initializing simulator...")
        self.PWM_FREQ = pwm_freq
        self.verbose = verbose

        # Create I2C
        self.i2c = I2C(board.GP27, board.GP26)
        if self.verbose >= 2: print(f"I2C initialized, addresses found: {self.__portScan()}")

        # Create ADS and MCP objects
        self.ads = ADS.ADS1015(self.i2c)
        self.mcp = MCP.MCP4728(self.i2c)
        if verbose: print("Initialized I2C devices")

        # Create the Halogen object
        self.hal = PWMOut(board.GP28, frequency=self.PWM_FREQ, duty_cycle=0, variable_frequency=True)
        if verbose: print(f"Initialized PWM at {self.PWM_FREQ}Hz")
        
        self.uv_safe = True
        self.therm_safe = True
        if verbose: print("Solar Simulator initialized")
	
    # Sets the LEDs and halogen brightness as a 16-bit integer value
    def setLEDs(self, r: int = 0, g: int = 0, b: int = 0, uv: int = 0, h: int = 0):
        self.mcp.channel_a.value = r
        self.mcp.channel_b.value = g
        self.mcp.channel_c.value = b
        self.mcp.channel_d.value = uv * (not self.uv_safe)
        self.hal.duty_cycle = h

        if self.verbose >= 2: print(f"RED: {self.mcp.channel_a.value}, GRN: {self.mcp.channel_b.value}, BLU: {self.mcp.channel_c.value}, UV: {self.mcp.channel_d.value}, HAL: {self.hal.duty_cycle}")
        elif self.verbose >= 1: print(f"RED: {self.mcp.channel_a.value // 655}%, GRN: {self.mcp.channel_b.value // 655}%, BLU: {self.mcp.channel_c.value // 655}%, UV: {self.mcp.channel_d.value // 655}%, HAL: {self.hal.duty_cycle // 655}%")
    
    # Returns a list of thermal values per thermistor channel in Celsius
    def checkThermals(self) -> list:
        thermals = []
        thermistors = self.__readThermistors()
        for chan, i in zip(thermistors, range(3)):
            thermals.append(chan[2])
            if self.verbose == 1: print(f"Channel[{i}]: {chan[2]}C")
        return thermals


    # Helper function that prints all available I2C devices
    def __portScan(self) -> list:
        self.i2c.try_lock()
        found = self.i2c.scan()
        self.i2c.unlock()
        return [hex(i) for i in found]

    # Helper function that reads all of the thermistors and returns a list of lists of data for each channel
    # Output: [[CHAN0 binary data, voltage, celsius temp], [CHAN1 binary data, voltage, celsius temp], [CHAN2 binary data, voltage, celsius temp]]
    def __readThermistors(self) -> list:
        therm_values = []
        for i in range(0,3):
            chan = AnalogIn(self.ads, i)
            therm_values.append([chan.value>>4, chan.voltage, self.__calculateTemp(chan.voltage)])
            if self.verbose >= 2: print(f"Channel[{i}]: {chan.value>>4}, {chan.voltage}v, {self.__calculateTemp(chan.voltage)}C")
        return therm_values

    # Helper function that takes a thermistor's voltage and returns it's temperature in Celsius
    def __calculateTemp(self, adc: float) -> float:
        if adc == 0: return None
        rth = (10000) * (3.3 / adc) - 10000
        therm = 1 / ((np.log(rth/10000) / 3977) + (1/298.15))
        return therm - 273.15


def calcSteps(limiter: float = 1) -> list:
    # Calculate the interpolation steps from a set intensity limiter (docs coming soon :tm:)
    red_min = 10756
    grn_min = 10140
    blu_min = 10620
    uv_min  = 10620
    pwm_min = 0
    red_max = int(MAX_VALUE * limiter)
    grn_max = int(MAX_VALUE * limiter)
    blu_max = int(MAX_VALUE * limiter)
    uv_max  = int(MAX_VALUE * limiter)
    pwm_max = int(MAX_VALUE * limiter)
    
    # Calculate steps between minimum and maximum values
    red_steps = np.linspace(red_min, red_max, num=101, dtype=np.uint16)
    grn_steps = np.linspace(grn_min, grn_max, num=101, dtype=np.uint16)
    blu_steps = np.linspace(blu_min, blu_max, num=101, dtype=np.uint16)
    uv_steps  = np.linspace( uv_min,  uv_max, num=101, dtype=np.uint16)
    pwm_steps = np.linspace(pwm_min, pwm_max, num=101, dtype=np.uint16)

    return [red_steps, grn_steps, blu_steps, uv_steps, pwm_steps]
