"""Entrypoint for the solar simulator."""

import os

from lib.app import SolarSimulatorApp
from lib.solar_simulator import SolarSimulator

build_mode = os.getenv("BUILD_MODE", "headless")


def main() -> None:
    """Start the main loop."""
    sim = SolarSimulator()
    sim.set_leds(0, 0, 0, 0)

    app = SolarSimulatorApp(sim)
    app.run(build_mode)


if __name__ == "__main__":
    main()
