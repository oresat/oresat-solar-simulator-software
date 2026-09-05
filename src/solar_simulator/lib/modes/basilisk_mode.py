"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys
import time

import supervisor

from ..solar_simulator import SolarSimulator as Sim
from ..utils import calculate_light_intensity, check_temperature, display_status


class BasiliskMode:
    """Implements the Basilisk Mode functionality with UART communication for CircuitPython."""

    def __init__(self, sim: Sim) -> None:
        """Initialize basilisk mode."""
        self.sim = sim

    def run(self) -> None:
        """Run basilisk mode loop."""
        print("Entering Basilisk Mode, waiting for input ...")
        buffer = ""
        try:
            while True:
                if supervisor.runtime.serial_bytes_available:
                    buffer += sys.stdin.read(1)

                    if "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        self.apply_line(line.replace("\x00", "").strip())
                        time.sleep(0.1)

        except KeyboardInterrupt:
            print("Keyboard interrupt caught, exiting Basilisk Mode loop.")

        print("Exiting Basilisk Mode.")

    def apply_line(self, line: str) -> None:
        """Apply one line of the Basilisk protocol: a bare integer from 0 to 100.

        A bad line is reported and skipped, so that a stray byte on the wire
        cannot take down an unattended run.
        """
        try:
            intensity = int(line)
        except ValueError:
            print(f"Invalid intensity value received: {line}")
            return

        if not 0 <= intensity <= 100:
            print(f"Invalid intensity value received: {intensity}")
            return

        intensity_values = calculate_light_intensity(intensity / 100)
        violet = int(intensity_values["Violet"] * 655)
        white = int(intensity_values["White"] * 655)
        cyan = int(intensity_values["Cyan"] * 655)
        halogen = int(intensity_values["Halogen"] * 655)

        self.sim.set_leds(v=violet, w=white, c=cyan, h=halogen)

        print(f"BasiliskMode: Intensity={intensity}", end="\n")
        check_temperature(self.sim)
        display_status(self.sim)
