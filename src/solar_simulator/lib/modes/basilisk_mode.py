"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys
import time

import supervisor

from ..solar_simulator import SolarSimulator as Sim
from ..utils import calculate_light_intensity, check_temperature


class BasiliskMode:
    """Implements the Basilisk Mode functionality with UART communication for CircuitPython."""

    def __init__(self, sim: Sim) -> None:
        """Initialize basilisk mode."""
        self.sim = sim
        self._warned = False

    def run(self) -> None:
        """Run basilisk mode loop."""
        buffer = ""
        while True:
            if supervisor.runtime.serial_bytes_available:
                buffer += sys.stdin.read(1)

                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.apply_line(line)
                    time.sleep(0.1)

    def apply_line(self, line: str) -> None:
        """Apply one line of the Basilisk protocol: a bare integer from 0 to 100.

        Answers with exactly one response line, so that a stray byte on the wire cannot
        take down an unattended run:

            OK <intensity>              the value was applied
            ERR <CODE> <description>    the line could not be acted on; CODE is the token
                                        the caller branches on
            WARN THERMAL <description>  the value is valid and is now the pending setpoint,
                                        held off while thermal shutdown is active
        """
        line = line.replace("\x00", "").strip()

        if not line:
            print("ERR EMPTY no intensity value received")
            return

        try:
            intensity = int(line)
        except ValueError:
            print(f"ERR PARSE invalid intensity value received: {line}")
            return

        if not 0 <= intensity <= 100:
            print(f"ERR RANGE invalid intensity value received: {line}")
            return

        intensity_values = calculate_light_intensity(intensity / 100)
        violet = int(intensity_values["Violet"] * 655)
        white = int(intensity_values["White"] * 655)
        cyan = int(intensity_values["Cyan"] * 655)
        halogen = int(intensity_values["Halogen"] * 655)

        self.sim.set_leds(v=violet, w=white, c=cyan, h=halogen)

        # The console carries protocol lines only: the shared cooldown chatter is
        # dropped, and the shutdown it announces is answered as WARN instead.
        self._warned = False
        check_temperature(
            self.sim,
            writer=lambda _message: None,
            on_shutdown=self._report_thermal_shutdown,
        )

        if not self._warned:
            print(f"OK {intensity}")

    def _report_thermal_shutdown(self) -> None:
        """Answer the line with a thermal warning."""
        self._warned = True
        print("WARN THERMAL temperature too high, lights off for safety")
