try:
    from ulab import numpy as np  # Use ulab when running on Pico
except ImportError:
    import numpy as np  # Use numpy when running on PC
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
    def __init__(self, pwm_freq: int = 5000, verbose: int = 0):
        # Initialize constants
        if verbose: print("Initializing simulator...")
        self.PWM_FREQ = pwm_freq
        self.verbose = verbose
        self.peak = 0.3
        self.i2c = I2C(board.GP27, board.GP26)
        if self.verbose >= 2: print(f"I2C initialized, addresses found: {self.__portScan()}")
        # Create ADS and MCP objects
        self.ads = ADS.ADS1015(self.i2c)
        self.mcp = MCP.MCP4728(self.i2c)
        if verbose: print("Initialized I2C devices")

        # Create the Halogen object
        self.hal = PWMOut(board.GP28, frequency=self.PWM_FREQ, duty_cycle=0, variable_frequency=True)
        if verbose: print(f"Initialized PWM at {self.PWM_FREQ}Hz")

        self.uv_safety = True
        self.therm_safe = True
        # Initialize current light settings to zero
        self.current_light_settings = {
            'v': 0,
            'w': 0,
            'c': 0,
            'uv': 0,  # (**abandon**)
            'h': 0
        }
        self.enable_therm_monitoring = True
        self.therm_led_shutdown = 100
        self.therm_heatsink_shutdown = 60
        self.therm_cell_shutdown = 80
        self.therm_resume_temp = 45

        if verbose: print("Solar Simulator initialized")

    # Sets the LEDs and halogen brightness as a 16-bit integer value
    def setLEDs(self, v: int = 0, w: int = 0, c: int = 0, uv: int = 0, h: int = 0):
        self.mcp.channel_a.value = v
        self.mcp.channel_b.value = w
        self.mcp.channel_c.value = c
        self.mcp.channel_d.value = uv * (not self.uv_safety)
        self.hal.duty_cycle = h

        # Update current settings
        self.current_light_settings = {
            'v': v,
            'w': w,
            'c': c,
            'uv': uv if not self.uv_safety else 0,  # (**abandon**)
            'h': h
        }
        if self.verbose >= 2:
            print(
                f"VIOLET: {self.mcp.channel_a.value}, WHITE: {self.mcp.channel_b.value}, CYAN: {self.mcp.channel_c.value}, UV: {self.mcp.channel_d.value}, HAL: {self.hal.duty_cycle}")
        elif self.verbose >= 1:
            print(
                f"VIOLET: {self.mcp.channel_a.value // 655}%, WHITE: {self.mcp.channel_b.value // 655}%, CYAN: {self.mcp.channel_c.value // 655}%, UV: {self.mcp.channel_d.value // 655}%, HAL: {self.hal.duty_cycle // 655}%")

    #65535，percentage just do that
    # Returns a list of thermal values per thermistor channel in Celsius
    def checkThermals(self) -> list:
        thermals = []
        thermistors = self.__readThermistors()
        for i, chan in zip(range(3), thermistors):
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
        for i in range(0, 3):
            chan = AnalogIn(self.ads, i)
            therm_values.append([chan.value >> 4, chan.voltage, calcTemp(chan.voltage)])
            if self.verbose >= 2: print(f"Channel[{i}]: {chan.value >> 4}, {chan.voltage}v, {calcTemp(chan.voltage)}C")
        return therm_values


# Helper function that takes a thermistor's voltage and returns it's temperature in Celsius
import math

def calcTemp(v_adc: float, vcc: float = 3.3, r_fixed: float = 10000.0) -> float | None:
    """
    Convert ADC voltage reading to temperature in Celsius using:
    - Voltage divider formula
    - Beta parameter equation (simplified Steinhart-Hart)
    """

    # Edge case: prevent divide-by-zero
    if v_adc <= 0 or v_adc >= vcc:
        return None

    # [1] Compute thermistor resistance
    r_therm = r_fixed * v_adc / (vcc - v_adc)

    # [2] Compute temperature using beta equation
    beta = 3977  # From datasheet (B25/85)
    t0 = 298.15  # Reference temperature in Kelvin (25°C)
    r0 = 10000.0  # Resistance at t0 (25°C)

    try:
        temp_k = 1.0 / ((math.log(r_therm / r0) / beta) + (1.0 / t0))
        temp_c = temp_k - 273.15
        return temp_c
    except ValueError:
        return None  # math domain error if log input is negative


def calcSteps(limiter: float = 1) -> list:
    # Define the sun spectrum proportions
    SUN_SPECTRUM = {
        "violet": 1,
        "white": 1,
        "cyan": 1,
        "uv": 1,  # (**abandon**)
        "halogen": 1
    }

    max_value = max(SUN_SPECTRUM.values())
    normalized_spectrum = {key: value / max_value for key, value in SUN_SPECTRUM.items()}

    total_min = 0
    total_max = int(MAX_VALUE * limiter)
    total_steps = np.linspace(total_min, total_max, num=101, dtype=np.uint16)

    violet_steps = np.array(total_steps * normalized_spectrum["violet"], dtype=np.uint16)
    white_steps = np.array(total_steps * normalized_spectrum["white"], dtype=np.uint16)
    cyan_steps = np.array(total_steps * normalized_spectrum["cyan"], dtype=np.uint16)
    uv_steps = np.array(total_steps * normalized_spectrum["uv"], dtype=np.uint16)  # (**abandon**)
    pwm_steps = np.array(total_steps * normalized_spectrum["halogen"], dtype=np.uint16)

    return [violet_steps, white_steps, cyan_steps, uv_steps, pwm_steps]
