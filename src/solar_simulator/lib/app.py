"""Solar Simulator Application."""

from .cli import Cli
from .solar_simulator import SolarSimulator as Sim


class SolarSimulatorApp:
    """Main application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator App."""
        self.sim = sim

    def run(self) -> None:
        """Run the Solar Simulator App."""
        Cli(self.sim).run()
