"""Solar Simulator Application.

The app is headless and speaks the following protocol over serial:

TODO: Document the solar sim app protocol.
"""

import sys

from .solar_simulator import SolarSimulator as Sim
from .utils import calculate_light_intensity


class SolarSimulatorApp:
    """The Solar Simulator Application."""

    def __init__(self, sim: Sim) -> None:
        """Initialize the solar simulator application."""
        self.sim = sim


    def run(self) -> None:
        """Listen for requests coming in through the console and parse each."""
        for req in sys.stdin:
            self.parse(req.rstrip("\n"))


    def parse(self, req: str) -> None:
        """Parse a given request (0 - 100) and print the response.

        OK <intensity>
        WARN THERMAL <description>
        ERR <CODE> <description>
        ERR THERMAL <description>
        """
        if not req:
            print("ERR EMPTY no intensity value received")
            return

        try:
            intensity = int(req)
        except ValueError:
            print(f"ERR PARSE invalid intensity value received: {req}")
            return

        if not 0 <= intensity <= 100:
            print(f"ERR RANGE intensity value out of range: {req}")
            return

        # TODO: ERR THERMAL

        # TODO: WARN THERMAL temperature too high, lights off for safety

        levels = calculate_light_intensity(intensity / 100)
        self.sim.set_leds(
            v=int(levels["Violet"] * 655),
            w=int(levels["White"] * 655),
            c=int(levels["Cyan"] * 655),
            h=int(levels["Halogen"] * 655),
        )
        print(f"OK {intensity}")
