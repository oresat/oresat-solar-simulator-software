# lib/modes/basilisk_mode.py

import time
import json
from ulab import numpy as np
from manual_mode import check_for_interrupt, check_temperature, display_status
from ..utils import calculate_light_intensity



class BasiliskMode:
    """
    Implements the Basilisk Mode functionality.
    """
    def __init__(self, sim):
        self.sim = sim
        self.bsk_data = None
        self.current_level = 0

    def run(self):
        print("Entering Basilisk Mode")

        with open('pico-demos/bsk_data_example/out.json', 'r') as jsonfile:
            bsk_dict = json.load(jsonfile)

        self.bsk_data = np.array(bsk_dict['0'])

        try:
            while True:
                intensity = int(self.bsk_data[self.current_level])

                intensity_values = calculate_light_intensity(intensity)
                red = int(intensity_values["Red"] * 655)
                green = int(intensity_values["Green"] * 655)
                blue = int(intensity_values["Blue"] * 655)
                halogen = int(intensity_values["Halogen"] * 655)
                uv = int(intensity_values["UV"] * 655)

                self.sim.setLEDs(r=red, g=green, b=blue, uv=uv, h=halogen)
                self.sim.current_light_settings = {
                    'r': red,
                    'g': green,
                    'b': blue,
                    'uv': uv,
                    'h': halogen
                }

                print(f"BasiliskMode: Intensity={intensity}, Level={self.current_level}", end="\n")

                check_for_interrupt()
                check_temperature(self.sim)
                display_status(self.sim)

                self.current_level += 1
                if self.current_level >= len(self.bsk_data):
                    self.current_level = 0

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Keyboard interrupt caught, exiting Basilisk Mode loop.")

        print("Exiting Basilisk Mode.")