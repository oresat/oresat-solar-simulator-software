"""Solar Simulator Application."""

from .modes.basilisk_mode import BasiliskMode
from .solar_simulator import SolarSimulator as Sim


class SolarSimulatorApp:
    """Main application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator App."""
        self.sim = sim

    def run(self, build_mode: str) -> None:
        """Run the Solar Simulator App for the given build mode.

        The `complete` build drops into the interactive menu for direct user access. Anything
        else runs headless, driven by intensity values streamed over serial.
        """
        if build_mode == "complete":
            from .cli import Cli  # noqa: PLC0415

            Cli(self.sim).run()
        else:
            BasiliskMode(self.sim).run()
