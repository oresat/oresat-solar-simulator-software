"""Solar Simulator Application.

The app is headless and uses a protocol that is simple for both humans and machines
to understand. See the README for protocol documentation.
"""

import sys

from .solar_simulator import SolarSimulator as Sim
from .solar_simulator import ThermalSensorError
from .utils import calculate_light_intensity, enforce_thermal_limits


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
        """Parse a given request (0 - 100) and print the response."""
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

        self.sim.set_leds(**calculate_light_intensity(intensity / 100))

        try:
            shut_down = enforce_thermal_limits(self.sim)
        except ThermalSensorError as error:
            self.sim.set_leds(0, 0, 0, 0)
            print(f"ERR THERMAL {error}")
            return

        if shut_down:
            print("WARN THERMAL temperature too high, lights off for safety")
        else:
            print(f"OK {intensity}")
