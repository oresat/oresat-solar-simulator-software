"""Entrypoint for the solar simulator."""

from lib.solar_simulator import SolarSimulator


def main() -> None:
    """Start the main loop."""
    sim = SolarSimulator()
    sim.set_leds(0, 0, 0, 0, 0)


if __name__ == "__main__":
    main()
