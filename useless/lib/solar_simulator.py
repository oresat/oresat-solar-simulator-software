# solar_simulator.py

try:
    from ulab import numpy as np  # Use ulab when running on Pico
except ImportError:
    import numpy as np  # Use numpy when running on PC
import adafruit_mcp4728 as MCP  # 12-bit DAC
import adafruit_ads1x15.ads1015 as ADS  # 4-channel ADC
from adafruit_ads1x15.analog_in import AnalogIn
from pwmio import PWMOut
import board

MAX_VALUE = 65535

class SolarSimulator:
    """
    SolarSimulator class controls the solar simulator hardware components.
    """

    def __init__(self, pwm_freq: int = 50000, verbose: int = 0):
        """
        Initializes the Solar Simulator module.
        """
        self.PWM_FREQ = pwm_freq
        self.verbose = verbose
        self.peak = 0.3
        self.i2c = board.I2C()
        if self.verbose >= 2:
            print(f"I2C initialized, addresses found: {self._port_scan()}")

        # Create ADS and MCP objects
        self.ads = ADS.ADS1015(self.i2c)
        self.mcp = MCP.MCP4728(self.i2c)
        if verbose:
            print("Initialized I2C devices")

        # Create the Halogen object
        self.hal = PWMOut(board.GP28, frequency=self.PWM_FREQ, duty_cycle=0, variable_frequency=True)
        if verbose:
            print(f"Initialized PWM at {self.PWM_FREQ}Hz")

        self.uv_safety = True
        self.therm_safe = True
        self.current_light_settings = {'r': 0, 'g': 0, 'b': 0, 'uv': 0, 'h': 0}
        if verbose:
            print("Solar Simulator initialized")

    def set_leds(self, r: int = 0, g: int = 0, b: int = 0, uv: int = 0, h: int = 0):
        """
        Sets the LEDs and halogen brightness as 16-bit integer values.
        """
        self.mcp.channel_a.value = r
        self.mcp.channel_b.value = g
        self.mcp.channel_c.value = b
        self.mcp.channel_d.value = uv * (not self.uv_safety)
        self.hal.duty_cycle = h

        self.current_light_settings = {'r': r, 'g': g, 'b': b, 'uv': uv, 'h': h}

        if self.verbose >= 2:
            print(f"RED: {r}, GRN: {g}, BLU: {b}, UV: {uv}, HAL: {h}")
        elif self.verbose >= 1:
            print(f"RED: {r // 655}%, GRN: {g // 655}%, BLU: {b // 655}%, UV: {uv // 655}%, HAL: {h // 655}%")

    def check_thermals(self) -> list:
        """
        Returns a list of thermal values per thermistor channel in Celsius.
        """
        thermals = []
        thermistors = self._read_thermistors()
        for i, chan in zip(range(3), thermistors):
            thermals.append(chan[2])
            if self.verbose == 1:
                print(f"Channel[{i}]: {chan[2]}C")
        return thermals

    def _port_scan(self) -> list:
        """
        Helper function that scans and returns all available I2C devices.
        """
        self.i2c.try_lock()
        found = self.i2c.scan()
        self.i2c.unlock()
        return [hex(i) for i in found]

    def _read_thermistors(self) -> list:
        """
        Helper function that reads all thermistors and returns their data.
        Output: [[CHAN0 binary data, voltage, celsius temp], ...]
        """
        therm_values = []
        for i in range(0, 3):
            chan = AnalogIn(self.ads, i)
            therm_values.append([chan.value >> 4, chan.voltage, calc_temp(chan.voltage)])
            if self.verbose >= 2:
                print(f"Channel[{i}]: {chan.value >> 4}, {chan.voltage}v, {calc_temp(chan.voltage)}C")
        return therm_values

def calc_temp(adc_voltage):
    """
    Calculates the temperature in Celsius from ADC voltage.

    :param adc_voltage: Voltage read from ADC
    :return: Temperature in Celsius
    """
    if adc_voltage == 0:
        return None
    rth = (10000) * (3.3 / adc_voltage) - 10000
    therm = 1 / ((np.log(rth / 10000) / 3977) + (1 / 298.15))
    return therm - 273.15
