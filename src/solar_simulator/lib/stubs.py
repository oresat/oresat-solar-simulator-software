"""Stubs for the solar simulator hardware to test on a plain RP2040 microcontroller.

A Raspberry Pi Pico with no solar simulator attached has no pull-up resistors on
the I2C lines, so `busio.I2C` refuses to come up. These stubs exist so that the
app and its serial protocol can be exercised on a plain RP2040.
"""


class StubI2C:
    """Stand-in for `busio.I2C`."""


class StubADS1015:
    """Stand-in for `adafruit_ads1x15.ads1015`."""

    gain = 1
    bits = 12

    def read(self, _pin: int) -> int:
        """Return a room temperature reading."""
        return 13200


class StubChannel:
    """Stand-in for one `adafruit_mcp4728.Channel`."""

    def __init__(self) -> None:
        """Start the channel at zero, as the DAC does on power up."""
        self.value = 0


class StubMCP4728:
    """Stand-in for `adafruit_mcp4728.MCP4728`.

    Each channel records what was last written to it. The stub does not model the
    DAC's 12-bit quantization, so it reports back exactly what it was given.
    """

    def __init__(self) -> None:
        """Bring up the three channels the light board drives."""
        self.channel_a = StubChannel()
        self.channel_b = StubChannel()
        self.channel_c = StubChannel()


class StubPWMOut:
    """Stands in for `pwmio.PWMOut`."""

    def __init__(self) -> None:
        """Start with the halogen channel off."""
        self.duty_cycle = 0
