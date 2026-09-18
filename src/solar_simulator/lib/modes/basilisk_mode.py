"""Solar Simulator App 'Basilisk Mode' helper module."""

import sys

from ..solar_simulator import SolarSimulator as Sim
from ..solar_simulator import ThermalSensorError


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

        Every line is answered as soon as it is read. Nothing here blocks, so a caller
        waiting on a response never waits longer than one reading of the thermistors.

        OK <intensity>              the value was applied
        ERR <CODE> <description>    the line could not be acted on; CODE is the token
                                    the caller branches on
        WARN THERMAL <description>  the value was not applied. The simulator is in
                                    thermal shutdown with the lights off and stays that
                                    way until it cools, so send the value again later.
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

        # Asked before the value is applied, so a simulator that is already too hot is
        # never commanded brighter and the warning means exactly "not applied".
        try:
            too_hot = self.sim.in_thermal_shutdown()
        except ThermalSensorError as error:
            self.sim.set_leds(0, 0, 0, 0)
            print(f"ERR THERMAL {error}")
            return

        if too_hot:
            self.sim.blank_out()
            print("WARN THERMAL temperature too high, lights off for safety")
            return

        self.sim.set_intensity(intensity / 100)
        print(f"OK {intensity}")
