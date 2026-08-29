"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys
import time

import supervisor

from ..solar_simulator import SolarSimulator as Sim
from ..utils import calculate_light_intensity, check_temperature, display_status


class BasiliskMode:
    """Drive the simulator from intensity values streamed over serial."""

    def __init__(self, sim: Sim) -> None:
        """Initialize basilisk mode."""
        self.sim = sim

    def read(self) -> str:
        """Return any pending input, decoded, or an empty string if there is none."""
        return sys.stdin.read(1) if supervisor.runtime.serial_bytes_available else ""

    def write(self, message: str) -> None:
        """Emit a single line of output.

        This function is a thin wrapper to allow inheriting classes to use other
        means of writing commands to the solar simulator.
        """
        print(message)

    def run(self) -> None:
        """Run the intensity loop until the peer disconnects or sends a bad line."""
        buffer = ""
        try:
            while True:
                buffer += self.read()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if not self.handle_line(line):
                        return

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("BasiliskMode: interrupted, shutting down.")
        finally:
            self.sim.set_leds(0, 0, 0, 0)

    def handle_line(self, line: str) -> bool:
        """Apply one line of input, returning False when the loop should stop."""
        line = line.replace("\x00", "").strip()

        if not line:
            return False

        try:
            intensity = int(line)
        except ValueError:
            print(f"ERR invalid line: {line!r}")
            return False

        if not 0 <= intensity <= 100:
            print(f"ERR intensity out of range: {intensity}")
            return False

        levels = calculate_light_intensity(intensity / 100)
        channels = ("Violet", "White", "Cyan", "Halogen")
        v, w, c, h = (int(levels[channel] * 655) for channel in channels)

        self.sim.set_leds(v=v, w=w, c=c, h=h)
        self.sim.current_light_settings = {'v': v, 'w': w, 'c': c, 'h': h}

        check_temperature(self.sim)
        display_status(self.sim, writer=self.write)
        return True
