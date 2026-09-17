"""Solar Simulator App 'Auto Mode' helper module."""

import time

from ulab import numpy as np

from ..solar_simulator import SolarSimulator as Sim
from ..utils import (
    ThermalSensorError,
    calculate_light_intensity,
    check_for_interrupt,
    display_status,
    enforce_thermal_limits,
)


class AutoMode:
    """Auto Mode helper class for Solar Simulator App."""

    def __init__(self, sim: Sim) -> None:
        """Initialize auto mode."""
        self.sim = sim
        self.peak = 0.5

    def run(self) -> None:
        """Run auto mode loop."""
        print("Entering Auto Mode")
        max_intensity_input = input("Please enter the desired maximum light intensity (0 to 1): ")

        try:
            self.peak = float(max_intensity_input)
            if not (0 <= self.peak <= 1):
                raise ValueError("Intensity out of range.")  # noqa: TRY301
            print(f"Maximum light intensity set to: {self.peak}")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 1.")
            return

        # For reasonable accuracy, period should be between 10 seconds and ~1 hour 15 minutes
        period = int(input("Please enter desired period of sinusoid (at least 10, in seconds). "))
        if not (period >= 10):
            print("Invalid input. Please enter a number greater than 10.")
            return

        # Generate a sine wave pattern
        wave_array_length = 101
        wave = -np.cos(np.linspace(0, 2 * np.pi, wave_array_length))
        zeros = [0] * wave_array_length
        wave = np.maximum(wave, zeros)

        level = 0  # Initialize wave level index
        loop_time = period / wave_array_length  # average loop repetition time
        #  to get correct period

        try:
            loop_start = time.monotonic()

            while True:
                enforce_thermal_limits(self.sim)

                # Calculate current intensity factor
                intensity_factor = wave[level] * self.peak

                self.sim.set_leds(**calculate_light_intensity(intensity_factor))
                # Update level index for sine wave
                level = (level + 1) % len(wave)

                check_for_interrupt(self.sim)
                display_status(self.sim)

                # Adjust current repetition's timing as needed by sleeping
                before_sleep = time.monotonic() - loop_start
                time.sleep(loop_time - before_sleep % loop_time)

        except KeyboardInterrupt:
            print("\nExiting Auto Mode.")
            self.sim.set_leds(0, 0, 0, 0)
        except ThermalSensorError as error:
            print(f"\n{error}. Exiting Auto Mode.")
            self.sim.set_leds(0, 0, 0, 0)
