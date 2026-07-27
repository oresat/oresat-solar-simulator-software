"""The SolarSimulator module."""

import math

import adafruit_ads1x15.ads1015 as ads  # 4-channel ADC
import adafruit_mcp4728 as mcp  # 12-bit DAC
import board
from adafruit_ads1x15.analog_in import AnalogIn
from busio import I2C
from pwmio import PWMOut

MAX_VALUE = 65535


class SolarSimulator:
    """Simulates solar intensity through light device brightness.

    This class abstracts hardware control for the solar simulator lab device.
    """

    def __init__(self, pwm_freq: int = 5000) -> None:
        """Initialize the SolarSimulator."""
        self.PWM_FREQ = pwm_freq
        self.peak = 0.3
        self.i2c = I2C(board.GP27, board.GP26)
        self.ads = ads.ADS1015(self.i2c)
        self.mcp = mcp.MCP4728(self.i2c)
        self.hal = PWMOut(
            board.GP28,
            frequency=self.PWM_FREQ,
            duty_cycle=0,
            variable_frequency=True
        )
        self.uv_safety = True
        self.therm_safe = True
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


    def set_leds(self, v: int = 0, w: int = 0, c: int = 0, uv: int = 0, h: int = 0) -> None:
        """Set the light brightness levels and record the light configuration."""
        self.mcp.channel_a.value = v
        self.mcp.channel_b.value = w
        self.mcp.channel_c.value = c
        self.mcp.channel_d.value = uv * (not self.uv_safety)
        self.hal.duty_cycle = h
        self.current_light_settings = {
            'v': v,
            'w': w,
            'c': c,
            'uv': uv if not self.uv_safety else 0,  # (**abandon**)
            'h': h
        }


    def check_thermals(self) -> list:
        """Return a list of thermal values per thermistor channel in Celsius."""
        thermals = []
        thermistors = self._read_thermistors()

        for _i, chan in zip(range(3), thermistors, strict=True):
            thermals.append(chan[2])

        return thermals


    def _port_scan(self) -> list:
        """Print all available I2C devices."""
        self.i2c.try_lock()
        found = self.i2c.scan()
        self.i2c.unlock()

        return [hex(i) for i in found]


    def _read_thermistors(self) -> list:
        """Read all of the thermistors and returns a list of lists of data for each channel.

        Example Output:
        [[CHAN0 binary data, voltage, celsius temp],
         [CHAN1 binary data, voltage, celsius temp],
         [CHAN2 binary data, voltage, celsius temp]]
        """
        therm_values = []
        for i in range(3):
            chan = AnalogIn(self.ads, i)
            therm_values.append(
                [chan.value >> 4, chan.voltage, calc_temp(chan.voltage)]
            )

        return therm_values


def calc_temp(v_adc: float, vcc: float = 3.3, r_fixed: float = 10000.0) -> float | None:
    """Calculate the temperature."""
    # Compute thermistor resistance
    r_therm = r_fixed * v_adc / (vcc - v_adc)
    # Compute temperature using beta equation
    beta = 3977   # From datasheet (B25/85)
    t0 = 298.15   # Reference temperature in Kelvin (25°C)
    r0 = 10000.0  # Resistance at t0 (25°C)

    try:
        temp_k = 1.0 / ((math.log(r_therm / r0) / beta) + (1.0 / t0))
        return temp_k - 273.15
    except ValueError:
        return None
