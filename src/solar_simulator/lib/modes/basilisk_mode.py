"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys

from ..solar_simulator import SolarSimulator as Sim
from ..utils import ThermalSensorError, calculate_light_intensity, check_temperature


class BasiliskMode:
    """Implements the Basilisk Mode functionality with UART communication for CircuitPython."""

    def __init__(self, sim: Sim) -> None:
        """Initialize basilisk mode."""
        self.sim = sim

    def run(self) -> None:
        """Apply each line received on the console."""
        for line in sys.stdin:
            self.apply_line(line.rstrip("\n"))

    def apply_line(self, line: str) -> None:
        """Apply one line of the Basilisk protocol: an integer from 0 to 100.

        OK <intensity>              the value was applied
        ERR <CODE> <description>    the line could not be acted on; CODE is the token
                                    the caller branches on
        WARN THERMAL <description>  the value was applied, but the simulator was too hot
                                    to hold it; the lights were off until it cooled down
        """
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

        self.sim.set_leds(**calculate_light_intensity(intensity / 100))

        # The console carries protocol lines only: the shared cooldown chatter is
        # dropped, and the shutdown it announces is answered as WARN instead.
        try:
            shut_down = check_temperature(self.sim, writer=lambda _message: None)
        except ThermalSensorError as error:
            self.sim.set_leds(0, 0, 0, 0)
            print(f"ERR THERMAL {error}")
            return

        if shut_down:
            print("WARN THERMAL temperature too high, lights off for safety")
        else:
            print(f"OK {intensity}")
