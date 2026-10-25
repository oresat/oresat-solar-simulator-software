from __future__ import annotations

import asyncio.stream
import sys

from adafruit_mcp4728 import MCP4728
from pwmio import PWMOut


class Lights:
    """Simulates solar intensity through light device brightness.

    This class abstracts hardware control for the solar simulator lab device.
    """

    def __init__(self, dac: MCP4728, pwm: PWMOut) -> None:
        """Initialize the SolarSimulator."""
        self._pwm = pwm

        self._ch_violet = dac.channel_a
        self._ch_white = dac.channel_b
        self._ch_cyan = dac.channel_c

    def __enter__(self) -> Lights:
        self.set_intensity(0.0)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: None,
    ) -> None:
        self.set_intensity(0.0)

    @property
    def violet(self) -> int:
        return self._ch_violet.value

    @violet.setter
    def violet(self, value: int) -> None:
        if not 0 <= value <= 65535:
            raise ValueError(f"Violet out of range: {value}")
        self._ch_violet.value = value

    @property
    def white(self) -> int:
        return self._ch_white.value

    @white.setter
    def white(self, value: int) -> None:
        if not 0 <= value <= 65535:
            raise ValueError(f"White out of range: {value}")
        self._ch_white.value = value

    @property
    def cyan(self) -> int:
        return self._ch_cyan.value

    @cyan.setter
    def cyan(self, value: int) -> None:
        if not 0 <= value <= 65535:
            raise ValueError(f"Cyan out of range: {value}")
        self._ch_cyan.value = value

    @property
    def halogen(self) -> int:
        # Reading this property will return the value from the internal
        # representation, so it may differ from the value set
        return self._pwm.duty_cycle

    @halogen.setter
    def halogen(self, value: int) -> None:
        if not 0 <= value <= 65535:
            raise ValueError(f"Halogen out of range: {value}")
        self._pwm.duty_cycle = value

    def set_intensity(self, factor: float) -> None:
        """Calculate the sun calibrated light intensity values for every light."""
        if factor == 0.0:
            self.violet = 0
            self.white = 0
            self.cyan = 0
            self.halogen = 0
        elif 0.0 < factor <= 1.0:
            self.violet = int(-1.5066 * factor + 22.6663) * 655
            self.white = int(32.3521 * factor + 16.3331) * 655
            self.cyan = int(10.2647 * factor + 20.9998) * 655
            self.halogen = int(89.1446 * factor + 9.0003) * 655
        else:
            raise ValueError(f"Intensity must be between 0 and 1: {factor}")

    def __str__(self) -> str:
        v = self.violet
        w = self.white
        c = self.cyan
        h = self.halogen
        return f"VIOLET:{v // 655}% WHITE:{w // 655}% CYAN:{c // 655}%  HAL:{h // 655}%"

    def apply(self, line: str) -> str:
        if not line:
            return "ERR EMPTY no intensity value received"

        split = line.split()
        if len(split) == 1:
            try:
                intensity = float(*split)
            except ValueError:
                return f"ERR PARSE invalid intensity value received: {line}"
            try:
                self.set_intensity(intensity)
            except ValueError as e:
                return f"ERR INTENSITY {e}"
        elif len(split) == 4:
            try:
                raw = map(int, split)
            except ValueError:
                return f"ERR PARSE invalid intensity value received: {line}"

            try:
                self.violet, self.white, self.cyan, self.halogen = raw
            except ValueError as e:
                return f"ERR RAW {e}"
        else:
            return f"ERR INVALID: {line}"

        return f"OK {line}"

    async def run(self, therm: Thermal) -> None:
        stdin = asyncio.stream.Stream(sys.stdin)
        while True:
            line = await stdin.readline()
            if therm.cooling:
                print("ERR THERM thermal overheat")
            else:
                print(self.apply(line.decode().rstrip()))
