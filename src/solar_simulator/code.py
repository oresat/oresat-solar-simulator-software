"""Entrypoint for the solar simulator."""

from lib.modes.basilisk_mode import BasiliskMode
from lib.solar_simulator import SolarSimulator


def main() -> None:
    """Start the main loop."""
    sim = SolarSimulator()
    sim.set_leds(0, 0, 0, 0)

    BasiliskMode(sim).run()


if __name__ == "__main__":
    main()
