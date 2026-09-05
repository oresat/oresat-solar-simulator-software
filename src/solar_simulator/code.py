"""Entrypoint for the solar simulator."""

import os

from lib.app import SolarSimulatorApp
from lib.solar_simulator import SolarSimulator


def main() -> None:
    """Start the main loop."""
    sim = SolarSimulator()
    sim.set_leds(0, 0, 0, 0)

    app = SolarSimulatorApp(sim)
    app.run(os.getenv("BUILD_MODE", "headless"))


if __name__ == "__main__":
    main()
