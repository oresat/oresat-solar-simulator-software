# light_patterns.py

import time
import ulab.numpy as np  # Use ulab for numpy functionality
from utils import calculate_light_intensity, display_status

class LightPatterns:
    """
    Defines various light patterns and modes.
    """

    def __init__(self, simulator, temperature_monitor, input_handler):
        self.simulator = simulator
        self.temperature_monitor = temperature_monitor
        self.input_handler = input_handler

    def auto_mode(self):
        """
        Implements the Auto Mode functionality.
        """
        print("Entering Auto Mode")
        max_intensity_input = input("Please enter the desired maximum light intensity (0 to 1): ")
        try:
            self.simulator.peak = float(max_intensity_input)
            if self.simulator.peak < 0 or self.simulator.peak > 1:
                raise ValueError("Intensity out of range.")
            print(f"Maximum light intensity set to: {self.simulator.peak}")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 1.")
            return

        # Generate a sine wave pattern
        wave = np.sin(np.linspace(0, np.pi, 101))

        level = 0  # Initialize wave level index

        while True:
            if self.temperature_monitor.check_temperature():
                try:
                    # Calculate current intensity factor
                    intensity_factor = wave[level] * self.simulator.peak

                    # Calculate light intensities
                    intensity_values = calculate_light_intensity(intensity_factor)

                    # Scale values to PWM range (0 to 65535)
                    red = int(intensity_values["Red"] * 655)
                    green = int(intensity_values["Green"] * 655)
                    blue = int(intensity_values["Blue"] * 655)
                    halogen = int(intensity_values["Halogen"] * 655)
                    uv = int(intensity_values["UV"] * 655)

                    # Set LED intensities
                    self.simulator.set_leds(red, green, blue, uv, halogen)

                    # Update level index for sine wave
                    level = (level + 1) % len(wave)

                    # Display status
                    display_status(self.simulator)

                    # Check for keyboard interrupt
                    self.input_handler.check_for_interrupt()

                    # Pause for next wave step
                    time.sleep(1)

                except KeyboardInterrupt:
                    print("Exiting Auto Mode.")
                    break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
            else:
                print("Temperature too high! Lights turned off for safety.")
                break

    def manual_mode(self):
        """
        Implements the Manual Mode functionality.
        """
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
        Implements the Fixed Preset Mode.
        """
        intensity_input = 0.0  # Initialize light intensity
        while True:
            if self.temperature_monitor.check_temperature():
                try:
                    print(f"Current intensity: {intensity_input:.2f}")
                    user_input = input("Enter a value (0 to 1), or press Enter to increase intensity by 1%: ")

                    if user_input.strip() == "":
                        intensity_input = min(intensity_input + 0.01, 1.0)  # Increase by 1%, up to 1.0
                    else:
                        intensity_input = float(user_input)
                        if not (0 <= intensity_input <= 1):
                            print("Invalid intensity. Please enter a value between 0 and 1.")
                            continue

                    # Calculate light intensities
                    intensity_values = calculate_light_intensity(intensity_input)

                    # Extract light intensities and set LEDs
                    red = int(intensity_values["Red"] * 655)
                    green = int(intensity_values["Green"] * 655)
                    blue = int(intensity_values["Blue"] * 655)
                    halogen = int(intensity_values["Halogen"] * 655)
                    uv = int(intensity_values["UV"] * 655)

                    self.simulator.set_leds(r=red, g=green, b=blue, uv=uv, h=halogen)

                    # Temperature monitoring and light intensity display loop
                    while True:
                        if not self.temperature_monitor.check_temperature():
                            print("\nTemperature too high! Lights turned off for safety.")
                            self.simulator.set_leds(0, 0, 0, 0, 0)
                            break

                        display_status(self.simulator)
                        time.sleep(1)
                        self.input_handler.check_for_interrupt()

                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
            else:
                print("Temperature too high! Lights turned off for safety.")
                break

            command = input("Type 'exit' to quit or press Enter to continue: ").lower()
            if command == "exit":
                self.simulator.set_leds(0, 0, 0, 0, 0)
                break

    def manual_light_adjustment(self):
        """
        Implements Manual Light Source Adjustment.
        """
        while True:
            try:
                red = int(input("Enter red light intensity (0-65535): "))
                green = int(input("Enter green light intensity (0-65535): "))
                blue = int(input("Enter blue light intensity (0-65535): "))
                uv = int(input("Enter UV light intensity (0-65535): "))
                halogen = int(input("Enter halogen light intensity (0-65535): "))

                self.simulator.set_leds(r=red, g=green, b=blue, uv=uv, h=halogen)

                print("Lights set. Press Ctrl-C to stop.")
                while True:
                    self.input_handler.check_for_interrupt()
                    display_status(self.simulator)
                    self.temperature_monitor.check_temperature()
                    time.sleep(1)

            except ValueError:
                print("Invalid input. Please enter numeric values only.")
            except KeyboardInterrupt:
                print("\nExiting Manual Light Source Adjustment.")
                self.simulator.set_leds(0, 0, 0, 0, 0)
                break

    def wave_mode(self):
        """
        Implements the Wave Mode.
        """
        try:
            # Ask for manual light intensities for wave mode
            red = int(input("Enter peak red light intensity (0-65535): "))
            green = int(input("Enter peak green light intensity (0-65535): "))
            blue = int(input("Enter peak blue light intensity (0-65535): "))
            uv = int(input("Enter peak UV light intensity (0-65535): "))
            halogen = int(input("Enter peak halogen light intensity (0-65535): "))

            duration = float(input("Enter the wave duration in seconds: "))

            wave = np.concatenate((
                np.linspace(0, 1, 180),  # Upwards
                np.linspace(1, 0, 180)  # Downwards
            ))

            for level in wave:
                if self.temperature_monitor.check_temperature():
                    self.input_handler.check_for_interrupt()
                    self.simulator.set_leds(
                        r=int(red * level),
                        g=int(green * level),
                        b=int(blue * level),
                        uv=int(uv * level) if not self.simulator.uv_safety else 0,
                        h=int(halogen * level)
                    )
                    time.sleep(duration / 360)
                else:
                    print("Temperature too high! Exiting wave mode.")
                    self.simulator.set_leds(0, 0, 0, 0, 0)  # Ensure all lights are off
                    break

            print("Wave mode completed.")

        except ValueError:
            print("Invalid input. Please enter numeric values only.")
        except KeyboardInterrupt:
            print("\nExiting Wave Mode.")
            self.simulator.set_leds(0, 0, 0, 0, 0)

    def measurement_mode(self):
        """
        Implements the Measurement Mode.
        """
        print("Starting Measurement Mode...")
        lights = ["red", "green", "blue", "halogen"]
        levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Intensity levels

        for light in lights:
            print("\nMeasuring {} light...".format(light))
            for level in levels:
                print("Setting {} light to {}% intensity.".format(light, level))
                try:
                    # Convert percentage to PWM value (0-65535 scale)
                    pwm_value = int((level / 100) * 65535)

                    # Set only the current light, others set to 0
                    if light == "red":
                        self.simulator.set_leds(r=pwm_value, g=0, b=0, uv=0, h=0)
                    elif light == "green":
                        self.simulator.set_leds(r=0, g=pwm_value, b=0, uv=0, h=0)
                    elif light == "blue":
                        self.simulator.set_leds(r=0, g=0, b=pwm_value, uv=0, h=0)
                    elif light == "halogen":
                        self.simulator.set_leds(r=0, g=0, b=0, uv=0, h=pwm_value)

                    # Wait for user input to proceed
                    input("Press Enter to continue to the next intensity level...")

                    # Display current settings and check thermals
                    if self.temperature_monitor.check_temperature():
                        thermals = self.simulator.check_thermals()
                        if thermals:
                            led_temp, heatsink_temp, cell_temp = thermals
                            print("Temperature | LED: {:.1f}°C, Heatsink: {:.1f}°C, Cell: {:.1f}°C".format(
                                led_temp, heatsink_temp, cell_temp
                            ))
                        else:
                            print("Temperature sensors data not available.")
                    else:
                        print("Temperature too high! Exiting Measurement Mode.")
                        self.simulator.set_leds(0, 0, 0, 0, 0)
                        return

                except Exception as e:
                    print("Error during measurement for {} light at {}% intensity: {}".format(light, level, e))
            print("Completed measurement for {} light.".format(light))

        print("Measurement Mode completed.")

    def fine_tuning_adjustment(self):
        """
        Implements Fine-Tuning Adjustment.
        """
        print("Starting Fine-Tuning Adjustment Mode...")
        lights = ["red", "green", "blue", "uv", "halogen"]
        current_intensity = {light: 0 for light in lights}  # Track current intensity levels

        while True:
            print("\nCurrent Intensities:")
            for light in lights:
                print(f"  {light}: {current_intensity[light]}%")
            print("\nChoose a light to adjust or type 'exit' to return:")
            print("Options: red, green, blue, uv, halogen, exit")

            light = input("Your choice: ").lower()
            if light == "exit":  # Exit the mode
                print("Exiting Fine-Tuning Adjustment Mode.")
                self.simulator.set_leds(0, 0, 0, 0, 0)
                break
            elif light not in lights:
                print("Invalid choice. Please choose from 'red', 'green', 'blue', 'uv', 'halogen', or 'exit'.")
                continue

            print(f"Adjusting {light} light. Press Enter to increase by 1%, '+' to increase, '-' to decrease, or 'done' to finish.")
            while True:
                command = input("Enter command (default '+1%'): ").strip()
                if command == "done":  # Finish adjustment for the selected light
                    break
                elif command in ["+", ""]:  # '+' or Enter increases intensity
                    if current_intensity[light] < 100:
                        current_intensity[light] += 1
                        current_intensity[light] = min(current_intensity[light], 100)
                        # Update LEDs
                        self.simulator.set_leds(
                            r=int(current_intensity["red"] / 100 * 65535),
                            g=int(current_intensity["green"] / 100 * 65535),
                            b=int(current_intensity["blue"] / 100 * 65535),
                            uv=int(current_intensity["uv"] / 100 * 65535) if not self.simulator.uv_safety else 0,
                            h=int(current_intensity["halogen"] / 100 * 65535)
                        )
                        print(f"  {light} light set to {current_intensity[light]}%")
                    else:
                        print(f"  {light} light is already at maximum intensity (100%).")
                elif command == "-":  # Decrease intensity
                    if current_intensity[light] > 0:
                        current_intensity[light] -= 1
                        current_intensity[light] = max(current_intensity[light], 0)
                        # Update LEDs
                        self.simulator.set_leds(
                            r=int(current_intensity["red"] / 100 * 65535),
                            g=int(current_intensity["green"] / 100 * 65535),
                            b=int(current_intensity["blue"] / 100 * 65535),
                            uv=int(current_intensity["uv"] / 100 * 65535) if not self.simulator.uv_safety else 0,
                            h=int(current_intensity["halogen"] / 100 * 65535)
                        )
                        print(f"  {light} light set to {current_intensity[light]}%")
                    else:
                        print(f"  {light} light is already at minimum intensity (0%).")
                else:
                    print("Invalid input. Please press Enter, '+' or '-', or type 'done' to finish.")

    def basilisk_mode(self):
        """
        Implements the Basilisk Mode.
        """
        print("Entering Basilisk Mode")
        # Implement your Basilisk Mode functionality here
        print("Basilisk Mode is under development.")