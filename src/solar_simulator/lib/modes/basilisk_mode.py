"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys
import time

import supervisor

from ..solar_simulator import SolarSimulator as Sim
from ..utils import calculate_light_intensity, check_temperature


def _reading(thermals: list) -> str:
    """Render a thermal reading as trailing protocol fields, or nothing if none was taken."""
    if not thermals:
        return ""

    led, heatsink, cell = thermals
    return f" led={led:.1f} heatsink={heatsink:.1f} cell={cell:.1f}"


class BasiliskMode:
    """Implements the Basilisk Mode functionality with UART communication for CircuitPython."""

    def __init__(self, sim: Sim) -> None:
        """Initialize basilisk mode."""
        self.sim = sim
        self.buffer = ""

    def run(self) -> None:
        """Run basilisk mode loop."""
        while True:
            self.tick()

    def tick(self) -> None:
        """Advance the loop one step: take a waiting byte, and dispatch a finished line.

        Nothing here blocks, so the loop stays free to do something other than wait on the
        host between bytes.
        """
        if supervisor.runtime.serial_bytes_available:
            self.buffer += sys.stdin.read(1)

            if "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                self.receive(line)
                time.sleep(0.1)

    def receive(self, line: str) -> None:
        """Answer one line from the host."""
        self.apply_line(line)

    def apply_line(self, line: str) -> None:
        """Apply one line of the Basilisk protocol: a bare integer from 0 to 100.

        Answers with exactly one response line, so that a stray byte on the wire cannot
        take down an unattended run:

            OK <intensity> <reading>          the value was applied
            WARN THERMAL <intensity> <reading>
                                              the value is valid and is now the pending
                                              setpoint, held off while thermal shutdown
                                              is active
            ERR <CODE> <description>          the line could not be acted on; CODE is the
                                              token the caller branches on

        `OK` and `WARN` carry the reading the thermal decision was made on, as
        `led=<C> heatsink=<C> cell=<C>`. The token is the state and the temperatures say
        how far that state is from changing, so a host can tell a panel that is cooling
        from a board that has died (ADR-0007 in `brysat-flathils`). An `ERR` answers a
        line that never reached the thermal check, and carries no reading.
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

        # Driving the lamp while the panel is cooling would relight it until the check
        # below cut it again, once per line the host sends. Hold the value instead.
        if self.sim.therm_safe:
            self.sim.set_leds(v=violet, w=white, c=cyan, h=halogen)
        else:
            self.sim.pending_light_settings = {'v': violet, 'w': white, 'c': cyan, 'h': halogen}

        lit, thermals = check_temperature(self.sim)

        if lit:
            print(f"OK {intensity}{_reading(thermals)}")
        else:
            print(f"WARN THERMAL {intensity}{_reading(thermals)}")
