"""Entrypoint for the solar simulator."""

import board
from adafruit_ads1x15.ads1015 import ADS1015  # 4-channel ADC
from adafruit_mcp4728 import MCP4728  # 12-bit DAC
from busio import I2C
from lib.app import SolarSimulatorApp
from lib.solar_simulator import SolarSimulator
from lib.stubs import StubADS1015, StubI2C, StubMCP4728, StubPWMOut
from pwmio import PWMOut


def main() -> None:
    """Bring up the hardware and run the app."""
    try:
        i2c = I2C(board.GP27, board.GP26)
        ads = ADS1015(i2c)
        mcp = MCP4728(i2c)
        hal = PWMOut(board.GP28, frequency=5000, duty_cycle=0, variable_frequency=True)
    except (OSError, RuntimeError, ValueError) as err:
        # A board with no solar simulator attached has no pull-ups on the I2C
        # lines and nothing on the bus, so assume this is a regular RP2040 device
        # for testing purposes.
        print(f"WARN HARDWARE {err}; running on stub hardware")
        i2c = StubI2C()
        ads = StubADS1015()
        mcp = StubMCP4728()
        hal = StubPWMOut()

    sim = SolarSimulator(ads, hal, i2c, mcp)
    sim.set_leds(0, 0, 0, 0)

    app = SolarSimulatorApp(sim)
    app.run()


if __name__ == "__main__":
    main()
