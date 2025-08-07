# lib/modes/basilisk_mode.py

import time
import supervisor
import sys
from lib.modes.manual_mode import check_for_interrupt, check_temperature, display_status
from ..utils import calculate_light_intensity


class BasiliskMode:
    """
    Implements the Basilisk Mode functionality with UART communication for CircuitPython.
    """

    def __init__(self, sim):
        self.sim = sim

    def run(self):
        print("Entering Basilisk Mode, wait for data input")
        pre_data = None
        data = None
        buffer = ""
        try:
            while True:
                if supervisor.runtime.serial_bytes_available:
                    data = sys.stdin.read(1)
                    # print(f"data received: {repr(data)}")
                    buffer += data

                    if "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.replace("\x00", "").strip()
                        # print(f"Raw data received: {line}")
                        intensity = int(line)

                        if 0 <= intensity <= 100:
                            intensity_values = calculate_light_intensity(intensity / 100)
                            violet = int(intensity_values["Violet"] * 655)
                            white = int(intensity_values["White"] * 655)
                            cyan = int(intensity_values["Cyan"] * 655)
                            halogen = int(intensity_values["Halogen"] * 655)

                            self.sim.setLEDs(v=violet, w=white, c=cyan, h=halogen)
                            self.sim.current_light_settings = {
                                'v': violet,
                                'w': white,
                                'c': cyan,
                                'h': halogen
                            }

                            print(f"BasiliskMode: Intensity={intensity}", end="\n")
                            check_temperature(self.sim)
                            display_status(self.sim)
                        else:
                            print(f"Invalid intensity value received: {intensity}")

                        time.sleep(0.1)
                        buffer = ""

        except KeyboardInterrupt:
            print("Keyboard interrupt caught, exiting Basilisk Mode loop.")

        print("Exiting Basilisk Mode.")
