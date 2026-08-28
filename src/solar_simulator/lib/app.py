"""Solar Simulator Application."""

import usb_cdc

from .modes.basilisk_mode import BasiliskMode
from .solar_simulator import SolarSimulator as Sim


class SolarSimulatorApp:
    """Main application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator App."""
        self.sim = sim

    def run(self, build_mode: str) -> None:
        """Run the Solar Simulator App for a given build mode.

        Headless is the default build mode, which is optimized for integration
        with FlatHILS and Basilisk.
        """
        if build_mode == "complete":
            from .cli import Cli  # noqa: PLC0415

            cli = Cli(self.sim)
            cli.run()
        elif build_mode == "headless":
            headless = Headless(self.sim)
            headless.run()


class Headless(BasiliskMode):
    """Headless class.

    Runs the Basilisk loop over usb_cdc.
    """

    def __init__(self, sim: Sim) -> None:
        """Initialize headless mode."""
        super().__init__(sim)
        self.data = usb_cdc.data

    def read(self) -> str:
        """Drain the data endpoint's receive buffer."""
        return self.data.read(self.data.in_waiting).decode() if self.data.in_waiting else ""

    def write(self, message: str) -> None:
        """Emit a single line of output on the data endpoint."""
        self.data.write(f"{message}\n".encode())
