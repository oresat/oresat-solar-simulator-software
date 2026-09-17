"""The SolarSimulator module."""

from __future__ import annotations

import math

import adafruit_ads1x15.ads1015 as ads  # 4-channel ADC
import adafruit_mcp4728 as mcp  # 12-bit DAC
import board
from adafruit_ads1x15.analog_in import AnalogIn
from busio import I2C
from micropython import const
from pwmio import PWMOut

MAX_VALUE = const(65535)


class ThermalSensorError(Exception):
    """A thermistor could not be read, so its temperature is unknown."""


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
            board.GP28, frequency=self.PWM_FREQ, duty_cycle=0, variable_frequency=True
        )
        self.therm_safe = True
        self.current_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
        self.enable_therm_monitoring = True
        self.therm_led_shutdown = 100
        self.therm_heatsink_shutdown = 60
        self.therm_cell_shutdown = 80
        self.therm_resume_temp = 45

    def set_leds(self, v: int = 0, w: int = 0, c: int = 0, h: int = 0) -> None:
        """Set the light brightness levels and record the light configuration.

        The input values are 16-bit unsigned integers and use a default value of 0, so if
        nothing is entered into any of the arguments, it will turn off that channel.
        """
        self._drive(v, w, c, h)
        self.current_light_settings = {'v': v, 'w': w, 'c': c, 'h': h}

    def set_intensity(self, factor: float) -> None:
        """Set every channel to the brightness this instrument's calibration gives `factor`.

        `factor` runs from 0, dark, to 1, the simulator's full rated output.
        """
        self.set_leds(**self._calc_channel_values(factor))

    def blank(self) -> None:
        """Drive every channel dark without forgetting what was asked for.

        Use it for a pause the simulator will come back from, such as waiting out a
        thermal shutdown. `set_leds(0, 0, 0, 0)` is the one to use when the lights should
        stay off, since it makes darkness the setting rather than an interruption of one.
        """
        self._drive(0, 0, 0, 0)

    def restore(self) -> None:
        """Drive the channels back to the setting recorded by the last `set_leds`."""
        self._drive(**self.current_light_settings)

    def _drive(self, v: int, w: int, c: int, h: int) -> None:
        """Write brightness levels to the hardware without recording them as the setting."""
        self.mcp.channel_a.value = v
        self.mcp.channel_b.value = w
        self.mcp.channel_c.value = c
        self.hal.duty_cycle = h

    def check_thermals(self) -> list:
        """Return a list of thermal values per thermistor channel in Celsius.

        The returned list contains 3 temperatures in Celsius as a `float`.
            - `check_thermals()[0]` - Thermistor located at the SMT LEDs under the lid PCB
            - `check_thermals()[1]` - Thermistor attached to the heatsink on the top
            - `check_thermals()[2]` - Thermistor located where the solar cell is placed

        Raise ThermalSensorError when a thermistor cannot be read.
        """
        thermals = []
        thermistors = self._read_thermistors()

        for _i, chan in zip(range(3), thermistors):
            thermals.append(chan[2])

        return thermals

    def is_within_shutdown_limits(self, temperatures: list) -> bool:
        """Return whether every temperature is at or below its own shutdown limit.

        Each part carries its own tolerance, so each is compared against its own
        threshold. Its counterpart, `is_within_resume_limit`, deliberately shares one
        threshold across all three: the question there is whether the enclosure as a
        whole has settled, not whether each part is individually survivable.
        """
        led_temp, heatsink_temp, cell_temp = temperatures
        within_limits = (
            led_temp <= self.therm_led_shutdown,
            heatsink_temp <= self.therm_heatsink_shutdown,
            cell_temp <= self.therm_cell_shutdown,
        )

        return all(within_limits)

    def is_within_resume_limit(self, temperatures: list) -> bool:
        """Return whether every temperature is back at or below the shared resume limit."""
        return all(temp <= self.therm_resume_temp for temp in temperatures)

    def _port_scan(self) -> list:
        """Print all available I2C devices."""
        self.i2c.try_lock()
        found = self.i2c.scan()
        self.i2c.unlock()

        return [hex(i) for i in found]

    def _read_thermistors(self) -> list:
        """Read all of the thermistors and return a nested list of data for each channel.

        Example Output:
        [[CHAN0 binary data, voltage, celsius temp],
         [CHAN1 binary data, voltage, celsius temp],
         [CHAN2 binary data, voltage, celsius temp]]
        """
        therm_values = []
        for i in range(3):
            chan = AnalogIn(self.ads, i)
            therm_values.append([chan.value >> 4, chan.voltage, self._calc_temp(chan.voltage)])

        return therm_values

    @staticmethod
    def _calc_channel_values(factor: float) -> dict:
        """Given an intensity factor from 0 to 1, return the `set_leds` value per channel.

        The coefficients come from calibrating this instrument's four light sources against
        a reference cell, so they describe this hardware rather than solar simulation in
        general, and belong with the hardware they were measured from.
        """
        if not (0 <= factor <= 1):
            raise ValueError("Scaling factor must be between 0 and 1.")

        if factor == 0:
            violet_intensity = 0
            white_intensity = 0
            cyan_intensity = 0
            halogen_intensity = 0
        else:
            violet_intensity = -1.5066 * factor + 22.6663
            white_intensity = 32.3521 * factor + 16.3331
            cyan_intensity = 10.2647 * factor + 20.9998
            halogen_intensity = 89.1446 * factor + 9.0003

        return {
            'v': int(violet_intensity * 655),
            'w': int(white_intensity * 655),
            'c': int(cyan_intensity * 655),
            'h': int(halogen_intensity * 655),
        }

    @staticmethod
    def _calc_temp(v_adc: float, vcc: float = 3.3, r_fixed: float = 10000.0) -> float:
        """Given thermistor resistance, calculuate and return temperature (in Celsius).

        Raise ThermalSensorError when the voltage sits at or past either rail. That is a
        disconnected or shorted thermistor, not a very cold or very hot one: the divider
        cannot produce those voltages while a thermistor is attached to it.
        """
        if not 0 < v_adc < vcc:
            raise ThermalSensorError(f"Thermistor voltage out of range: {v_adc:.3f}V")

        # Thermistor resistance
        r_therm = r_fixed * v_adc / (vcc - v_adc)

        # Compute temperature (beta equation)
        beta = 3977  # From datasheet (B25/85)
        t0 = 298.15  # Reference temperature in Kelvin (25°C)
        r0 = 10000.0  # Resistance at t0 (25°C)
        temp_k = 1.0 / ((math.log(r_therm / r0) / beta) + (1.0 / t0))

        return temp_k - 273.15
