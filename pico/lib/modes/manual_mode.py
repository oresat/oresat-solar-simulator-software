# lib/modes/manual_mode.py

import time
import sys
import supervisor
from ulab import numpy as np
from ..utils import (
    calculate_light_intensity,
    display_status,
    check_temperature,
    check_for_interrupt
)

class ManualMode:
    """
    Implements the Manual Mode functionality.
    """
    def __init__(self, sim):
        self.sim = sim

    def run(self):
        print("Entering Manual Mode")
        print("Choose your manual control mode:")
        print("1. Fixed Preset Mode")
        print("2. Manual Light Source Adjustment")
        while True:
            choice = input("Your choice (input 1 or 2): ")
            if choice in ["1", "2"]:
                break
            else:
                print("Invalid input. Please enter 1 or 2.")

        if choice == '1':
            self.fixed_preset_mode()
        elif choice == '2':
            self.manual_light_adjustment()

    def fixed_preset_mode(self):
        """
        Fixed Preset Mode
        """
        print("Enter an initial intensity value (0 to 1).")
        print("Type 'exit' to return to the main menu.")

        while True:
            user_input = input("Please enter initial intensity (default is 0.0): ").strip()

            if user_input.lower() == 'exit':
                print("Exiting to the main menu.")
                self.sim.setLEDs(0, 0, 0, 0)
                return

            if user_input == "":
                intensity_input = 0.0
                break
            else:
                try:
                    intensity_input = float(user_input)
                    if not (0 <= intensity_input <= 1):
                        print("Invalid intensity. Please enter a value between 0 and 1.")
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")

            intensity_values = calculate_light_intensity(intensity_input)
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
            print(f"\nCurrent intensity: {intensity_input:.2f}")
            print("Press 'Enter' to reset your LEDs...")
            print("Type 'exit' to return to the main menu.")
            input_line = ""

            while True:
                check_for_interrupt()
                check_temperature(self.sim)
                display_status(self.sim)

                # Non-blocking user input detection
                if supervisor.runtime.serial_bytes_available:
                    c = sys.stdin.read(1)
                    if c == '\n' or c == '\r':
                        user_command = input_line.strip().lower()

                        if user_command == 'exit':
                            print("Exiting to the main menu.")
                            self.sim.setLEDs(0, 0, 0, 0)
                            return
                        else:
                            print("Returning to light intensity input.")
                            break
                    else:
                        input_line += c
                time.sleep(1)

    def manual_light_adjustment(self):
        """
        Manual Light Source Adjustment
        """
        while True:
            try:
                print("Enter light intensities. Type 'exit' to return to the main menu.")
                violet_input = input("Enter Violet light intensity: ")
                if violet_input.lower() == 'exit':
                    break
                white_input = input("Enter White light intensity: ")
                if white_input.lower() == 'exit':
                    break
                cyan_input = input("Enter Cyan light intensity: ")
                if cyan_input.lower() == 'exit':
                    break
                halogen_input = input("Enter halogen light intensity: ")
                if halogen_input.lower() == 'exit':
                    break

                violet_intensity = float(violet_input)
                white_intensity = float(white_input)
                cyan_intensity = float(cyan_input)
                halogen_intensity = float(halogen_input)

                if not (0 <= violet_intensity <= 1 and 0 <= white_intensity <= 1 and
                        0 <= cyan_intensity <= 1 and 0 <= halogen_intensity <= 1):
                    print("Invalid input. Please enter values between 0 and 1.")
                    continue

                violet = int((violet_intensity) * 65535)
                white = int((white_intensity) * 65535)
                cyan = int((cyan_intensity) * 65535)
                halogen = int((halogen_intensity) * 65535)

                self.sim.setLEDs(v=violet, w=white, c=cyan, h=halogen)
                print("Lights set to the specified intensities.")
                self.sim.current_light_settings = {
                    'v': violet,
                    'w': white,
                    'c': cyan,
                    'h': halogen
                }
                input_line = ""
                print("Press 'Enter' to input new values, or 'exit' to return to the main menu.")

                while True:
                    check_for_interrupt()
                    check_temperature(self.sim)
                    display_status(self.sim)

                    if supervisor.runtime.serial_bytes_available:
                        c = sys.stdin.read(1)
                        if c == '\n' or c == '\r':
                            user_command = input_line.strip().lower()
                            input_line = ""

                            if user_command == 'exit':
                                print("Exiting to the main menu.")
                                self.sim.setLEDs(0, 0, 0, 0)
                                return
                            else:
                                print("Returning to light intensity input.")
                                break
                        else:
                            input_line += c
                    time.sleep(1)
            except ValueError:
                print("Invalid input. Please enter numeric values only.")
