# lib/modes/auto_mode.py

from ulab import numpy as np
import time
from ..utils import (
    calculate_light_intensity,
    display_status,
    check_temperature,
    check_for_interrupt
)
class AutoMode:
    """
    Implements the Auto Mode functionality.
    """
    def __init__(self, sim):
        self.sim = sim
        self.peak = 0.5  # Default peak intensity

    def run(self):
        print("Entering Auto Mode")
        max_intensity_input = input("Please enter the desired maximum light intensity (0 to 1): ")
        try:
            self.peak = float(max_intensity_input)
            if not (0 <= self.peak <= 1):
                raise ValueError("Intensity out of range.")
            print(f"Maximum light intensity set to: {self.peak}")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 1.")
            return

        # Generate a sine wave pattern
        wave = np.sin(np.linspace(0, np.pi, 101))
        level = 0  # Initialize wave level index

        try:
            while True:
                if check_temperature(self.sim):
                    # Calculate current intensity factor
                    intensity_factor = wave[level] * self.peak

                    # Calculate light intensities
                    intensity_values = calculate_light_intensity(intensity_factor)

                    # Scale values to PWM range (0 to 65535)
                    red = int(intensity_values["Red"] * 655)
                    green = int(intensity_values["Green"] * 655)
                    blue = int(intensity_values["Blue"] * 655)
                    halogen = int(intensity_values["Halogen"] * 655)
                    uv = int(intensity_values["UV"] * 655)

                    # Set LED intensities
                    self.sim.setLEDs(r=red, g=green, b=blue, uv=uv, h=halogen)
                    self.sim.current_light_settings = {
                        'r': red,
                        'g': green,
                        'b': blue,
                        'uv': uv,
                        'h': halogen
                    }
                    # Update level index for sine wave
                    level = (level + 1) % len(wave)

                    check_for_interrupt()
                    display_status(self.sim)
                    time.sleep(1)
                else:
                    print("Temperature too high! Lights turned off for safety.")
                    break
        except KeyboardInterrupt:
            print("\nExiting Auto Mode.")
            self.sim.setLEDs(0, 0, 0, 0, 0)
