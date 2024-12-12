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
        print("3. Wave Mode")
        print("4. Measurement Mode")
        print("5. Fine-Tuning Adjustment")
        while True:
            choice = input("Your choice (input 1, 2, 3, 4, or 5): ")
            if choice in ["1", "2", "3", "4", "5"]:
                break
            else:
                print("Invalid input. Please enter 1, 2, 3, 4, or 5.")

        if choice == '1':
            self.fixed_preset_mode()
        elif choice == '2':
            self.manual_light_adjustment()
        elif choice == '3':
            self.wave_mode()
        elif choice == '4':
            self.measurement_mode()
        elif choice == '5':
            self.fine_tuning_adjustment()

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
                self.sim.setLEDs(0, 0, 0, 0, 0)
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
                            self.sim.setLEDs(0, 0, 0, 0, 0)
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
                print("Enter light intensities as percentages (0-100). Type 'exit' to return to the main menu.")
                red_input = input("Enter red light intensity (%): ")
                if red_input.lower() == 'exit':
                    break
                green_input = input("Enter green light intensity (%): ")
                if green_input.lower() == 'exit':
                    break
                blue_input = input("Enter blue light intensity (%): ")
                if blue_input.lower() == 'exit':
                    break
                uv_input = input("Enter UV light intensity (%): ")
                if uv_input.lower() == 'exit':
                    break
                halogen_input = input("Enter halogen light intensity (%): ")
                if halogen_input.lower() == 'exit':
                    break

                # Convert input to float and validate
                red_percent = float(red_input)
                green_percent = float(green_input)
                blue_percent = float(blue_input)
                uv_percent = float(uv_input)
                halogen_percent = float(halogen_input)

                if not (0 <= red_percent <= 100 and 0 <= green_percent <= 100 and
                        0 <= blue_percent <= 100 and 0 <= uv_percent <= 100 and
                        0 <= halogen_percent <= 100):
                    print("Invalid input. Please enter values between 0 and 100.")
                    continue

                # Convert percentage to PWM value
                red = int((red_percent / 100) * 65535)
                green = int((green_percent / 100) * 65535)
                blue = int((blue_percent / 100) * 65535)
                uv = int((uv_percent / 100) * 65535)
                halogen = int((halogen_percent / 100) * 65535)

                self.sim.setLEDs(r=red, g=green, b=blue, uv=uv, h=halogen)
                print("Lights set to the specified intensities.")
                self.sim.current_light_settings = {
                    'r': red,
                    'g': green,
                    'b': blue,
                    'uv': uv,
                    'h': halogen
                }
                input_line = ""
                print("Press 'Enter' to input new values, or 'exit' to return to the main menu.")

                while True:
                    check_for_interrupt()
                    check_temperature(self.sim)
                    display_status(self.sim)

                    # Non-blocking user input detection
                    if supervisor.runtime.serial_bytes_available:
                        c = sys.stdin.read(1)
                        if c == '\n' or c == '\r':
                            user_command = input_line.strip().lower()
                            input_line = ""

                            if user_command == 'exit':
                                print("Exiting to the main menu.")
                                self.sim.setLEDs(0, 0, 0, 0, 0)
                                return
                            else:
                                print("Returning to light intensity input.")
                                break
                        else:
                            input_line += c

                    time.sleep(1)
            except ValueError:
                print("Invalid input. Please enter numeric values only.")

    def wave_mode(self):
        """
        Wave Mode with manual inputs
        """
        try:
            print("Enter peak light intensities as percentages (0-100).")
            red_percent = float(input("Enter peak red light intensity (%): "))
            green_percent = float(input("Enter peak green light intensity (%): "))
            blue_percent = float(input("Enter peak blue light intensity (%): "))
            uv_percent = float(input("Enter peak UV light intensity (%): "))
            halogen_percent = float(input("Enter peak halogen light intensity (%): "))
            duration = float(input("Enter the wave duration in seconds: "))

            # Validate inputs
            if not (0 <= red_percent <= 100 and 0 <= green_percent <= 100 and
                    0 <= blue_percent <= 100 and 0 <= uv_percent <= 100 and
                    0 <= halogen_percent <= 100):
                print("Invalid input. Please enter values between 0 and 100.")
                return

            # Convert percentage to PWM value
            red = int((red_percent / 100) * 65535)
            green = int((green_percent / 100) * 65535)
            blue = int((blue_percent / 100) * 65535)
            uv = int((uv_percent / 100) * 65535)
            halogen = int((halogen_percent / 100) * 65535)

            wave = np.concatenate((
                np.linspace(0, 1, 180),  # Upwards
                np.linspace(1, 0, 180)   # Downwards
            ))

            for level in wave:
                if check_temperature(self.sim):
                    check_for_interrupt()
                    self.sim.setLEDs(
                        r=int(red * level),
                        g=int(green * level),
                        b=int(blue * level),
                        uv=int(uv * level) if not self.sim.uv_safety else 0,
                        h=int(halogen * level)
                    )
                    time.sleep(duration / 360)
                else:
                    print("Temperature too high! Exiting wave mode.")
                    self.sim.setLEDs(0, 0, 0, 0, 0)  # Ensure all lights are off
                    break

            print("Wave mode completed.")
        except ValueError:
            print("Invalid input. Please enter numeric values only.")

    def measurement_mode(self):
        """
        Measurement Mode
        """
        print("Starting Measurement Mode...")
        lights = ["red", "green", "blue", "halogen"]
        levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Intensity levels

        for light in lights:
            print(f"\nMeasuring {light} light...")
            for level in levels:
                print(f"Setting {light} light to {level}% intensity.")
                try:
                    pwm_value = int((level / 100) * 65535)

                    # Set only the current light, others set to 0
                    if light == "red":
                        self.sim.setLEDs(r=pwm_value, g=0, b=0, uv=0, h=0)
                    elif light == "green":
                        self.sim.setLEDs(r=0, g=pwm_value, b=0, uv=0, h=0)
                    elif light == "blue":
                        self.sim.setLEDs(r=0, g=0, b=pwm_value, uv=0, h=0)
                    elif light == "halogen":
                        self.sim.setLEDs(r=0, g=0, b=0, uv=0, h=pwm_value)

                    input("Press Enter to continue to the next intensity level...")
                    self.sim.current_light_settings = {
                        'r': pwm_value,
                        'g': pwm_value,
                        'b': pwm_value,
                        'uv':pwm_value,
                        'h': pwm_value
                    }
                    if check_temperature(self.sim):
                        display_status(self.sim)
                    else:
                        print("Temperature too high! Exiting Measurement Mode.")
                        self.sim.setLEDs(0, 0, 0, 0, 0)
                        return
                except Exception as e:
                    print(f"Error during measurement for {light} light at {level}% intensity: {e}")
            print(f"Completed measurement for {light} light.")

        print("Measurement Mode completed.")

    def fine_tuning_adjustment(self):
        """
        Fine-Tuning Adjustment Mode
        """
        print("Starting Fine-Tuning Adjustment Mode...")
        lights = ["red", "green", "blue", "uv", "halogen"]
        current_intensity = {light: 0 for light in lights}

        while True:
            print("\nCurrent Intensities:")
            for light in lights:
                print(f"  {light}: {current_intensity[light]}%")
            print("\nChoose a light to adjust or type 'exit' to return:")
            print("Options: red, green, blue, uv, halogen, exit")

            light = input("Your choice: ").lower()
            if light == "exit":
                print("Exiting Fine-Tuning Adjustment Mode.")
                self.sim.setLEDs(0, 0, 0, 0, 0)
                break
            elif light not in lights:
                print("Invalid choice. Please choose from 'red', 'green', 'blue', 'uv', 'halogen', or 'exit'.")
                continue

            print(
                f"Adjusting {light} light. Press Enter to increase by 1%, '+' to increase, '-' to decrease, or 'done' to finish.")
            while True:
                command = input("Enter command (default '+1%'): ").strip()
                if command == "done":
                    break
                elif command in ["+", ""]:
                    if current_intensity[light] < 100:
                        current_intensity[light] += 1
                        current_intensity[light] = min(current_intensity[light], 100)
                        # Update LEDs
                        self.sim.setLEDs(
                            r=int(current_intensity["red"] / 100 * 65535),
                            g=int(current_intensity["green"] / 100 * 65535),
                            b=int(current_intensity["blue"] / 100 * 65535),
                            uv=int(current_intensity["uv"] / 100 * 65535) if not self.sim.uv_safety else 0,
                            h=int(current_intensity["halogen"] / 100 * 65535)
                        )
                        print(f"  {light} light set to {current_intensity[light]}%")
                    else:
                        print(f"  {light} light is already at maximum intensity (100%).")
                elif command == "-":
                    if current_intensity[light] > 0:
                        current_intensity[light] -= 1
                        current_intensity[light] = max(current_intensity[light], 0)
                        # Update LEDs
                        self.sim.setLEDs(
                            r=int(current_intensity["red"] / 100 * 65535),
                            g=int(current_intensity["green"] / 100 * 65535),
                            b=int(current_intensity["blue"] / 100 * 65535),
                            uv=int(current_intensity["uv"] / 100 * 65535) if not self.sim.uv_safety else 0,
                            h=int(current_intensity["halogen"] / 100 * 65535)
                        )
                        print(f"  {light} light set to {current_intensity[light]}%")
                    else:
                        print(f"  {light} light is already at minimum intensity (0%).")
                else:
                    print("Invalid input. Please press Enter, '+' or '-', or type 'done' to finish.")

        print("Fine-Tuning Adjustment Mode completed.")
