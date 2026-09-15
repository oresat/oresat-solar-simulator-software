"""Entrypoint for the solar simulator."""

import os

from lib.modes.basilisk_mode import BasiliskMode
from lib.solar_simulator import SolarSimulator


def main() -> None:
    """Start the main loop."""
    sim = SolarSimulator()
    sim.set_leds(0, 0, 0, 0)

    if os.getenv("BUILD_MODE", "headless") == "complete":
        # The headless build does not ship cli.mpy, so importing it at module level
        # would stop the board before it ever read a line.
        from lib.cli import Cli  # noqa: PLC0415

        Cli(sim).run()
    else:
        BasiliskMode(sim).run()


if __name__ == "__main__":
    main()
