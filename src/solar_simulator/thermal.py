import asyncio
import math

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn

class Thermal:
    _led_shutdown = 100
    _heatsink_shutdown = 60
    _cell_shutdown = 80

    _resume = 45

    def __init__(self, adc: ADS1015) -> None:
        self._cooling = False

        self._ch_led = AnalogIn(adc, 0)
        self._ch_heatsink = AnalogIn(adc, 1)
        self._ch_cell = AnalogIn(adc, 2)

    @staticmethod
    def _calc_temp(v_adc: float, vcc: float = 3.3, r_fixed: float = 10000.0) -> float:
        """Given a thermistor ADC sample, calculate and return temperature (in Celsius)."""
        # The thermistor should be between about 417kohm (-40C) and 350ohm (125C), the rated min
        # and max temperatures. In the voltage divider this results in v_adc between ~0.11V
        # and ~3.22V at 3.3V vcc. Outside of that range indicates a physical failure - e.g. v_adc
        # will drift up to vcc when the thermistor is unplugged. Also note that v_adc can read
        # slightly higher than 3.3V given variability in supply (I've seen 3.31) but a) there's no
        # way to measure this at runtime and b) v_adc >= vcc breaks the math below. v_adc <= 0 also
        # breaks the math.
        if v_adc > 0.977 * vcc:
            raise ValueError(f"Thermistor voltage too high: {v_adc:.3f}V - unplugged?")
        if v_adc < 0.033 * vcc:
            raise ValueError(f"Thermistor voltage too low: {v_adc:.3f}V - shorted?")

        # Thermistor resistance in the voltage divider
        r_therm = r_fixed * v_adc / (vcc - v_adc)

        # Compute temperature (beta equation)
        beta = 3977.0  # From datasheet (B25/85)
        t0 = 298.15  # Reference temperature in Kelvin (25°C)
        r0 = 10000.0  # Resistance at t0 (25°C)
        temp_k = 1.0 / ((math.log(r_therm / r0) / beta) + (1.0 / t0))

        return temp_k - 273.15

    @property
    def led(self) -> float:
        """Thermistor located at the SMT LEDs under the lid PCB in Celsius"""
        return self._calc_temp(self._ch_led.voltage)

    @property
    def heatsink(self) -> float:
        """Thermistor attached to the heatsink on the top in Celsius"""
        return self._calc_temp(self._ch_heatsink.voltage)

    @property
    def cell(self) -> float:
        """Thermistor located where the solar cell is placed in Celsius"""
        return self._calc_temp(self._ch_cell.voltage)

    def __str__(self) -> str:
        return f"LED: {self.led:.1f}°C, Heatsink: {self.heatsink:.1f}°C, Cell: {self.cell:.1f}°C"

    def _overheating(self) -> bool:
        return (
            self.led >= self._led_shutdown
            or self.heatsink >= self._heatsink_shutdown
            or self.cell >= self._cell_shutdown
        )

    def _cooled(self) -> bool:
        return self.led < self._resume and self.heatsink < self._resume and self.cell < self._resume

    @property
    def cooling(self) -> bool:
        return self._cooling

    async def run(self, lights: Lights) -> None:
        while True:
            if self._cooling:
                if self._cooled():
                    self._cooling = False
            elif self._overheating():
                self._cooling = True
                lights.set_intensity(0)

            await asyncio.sleep(1)
