# lib/utils.py

import time
import sys
import supervisor
from .solar_simulator import SolarSimulator as sim
# Constants and Configurations
def calculate_light_intensity(factor):
    """
    Calculate the light intensity values for 5 types of lights.
    """
    if not (0 <= factor <= 1):
        raise ValueError("Scaling factor must be between 0 and 1.")

    # Calculating intensities for each light source
    red_intensity = -1.5066 * factor + 22.6663
    green_intensity = 32.3521 * factor + 16.3331
    blue_intensity = 10.2647 * factor + 20.9998
    halogen_intensity = 89.1446 * factor + 9.0003
    uv_intensity = 16.7591 * factor + 22.0008

    # Storing the intensities in a dictionary
    intensities = {
        "Red": red_intensity,
        "Green": green_intensity,
        "Blue": blue_intensity,
        "Halogen": halogen_intensity,
        "UV": uv_intensity
    }

    return intensities

def display_status(sim):
    """
    Display the current thermal and light status.
    """
    try:
        thermals = sim.checkThermals()
        if thermals:
            led_temp, heatsink_temp, cell_temp = thermals
            temp_info = "LED: {:.1f}°C, Heatsink: {:.1f}°C, Cell: {:.1f}°C".format(led_temp, heatsink_temp, cell_temp)
        else:
            temp_info = "Cannot read temperature data"
    except Exception:
        temp_info = "Temperature data unavailable"

    # Get current light settings
    current_settings = sim.current_light_settings
    try:
        light_info = f"RED:{current_settings['r'] // 655}% GRN:{current_settings['g'] // 655}% BLU:{current_settings['b'] // 655}% UV:{(current_settings['uv'] // 655) if not sim.uv_safety else 0}% HAL:{current_settings['h'] // 655}%"
    except Exception:
        light_info = "Light data unavailable"

    print(f"{temp_info} | {light_info}", end="\n")

def input_with_default(prompt, default_value, valid_values=None, value_type=str):
    """
    Get user input with a default value and optional validation.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "":
            return default_value
        try:
            value = value_type(user_input)
            if valid_values and value not in valid_values:
                raise ValueError
            return value
        except ValueError:
            print(f"Invalid input. Please enter one of the following: {valid_values} or press Enter for default.")
        except Exception:
            print(f"Invalid input. Please enter a valid {value_type.__name__} value or press Enter for default.")

def check_temperature(sim):
    """
    Check the temperature and handle thermal shutdown and resume.
    """
    if not sim.enable_therm_monitoring:
        return True

    thermals = sim.checkThermals()
    if not thermals:
        print("Cannot read the temperature sensors")
        return False

    led_temp, heatsink_temp, cell_temp = thermals
    led_temp = led_temp or 0
    heatsink_temp = heatsink_temp or 0
    cell_temp = cell_temp or 0

    if (
        led_temp > sim.therm_led_shutdown
        or heatsink_temp > sim.therm_heatsink_shutdown
        or cell_temp > sim.therm_cell_shutdown
    ):
        previous_light_settings = sim.current_light_settings
        sim.setLEDs(0, 0, 0, 0, 0)
        print("Temperature too high! Turning off lights for safety.")

        while (
            led_temp > sim.therm_resume_temp
            and heatsink_temp > sim.therm_resume_temp
            and cell_temp > sim.therm_resume_temp
        ):
            time.sleep(1)
            thermals = sim.checkThermals()
            if thermals:
                led_temp, heatsink_temp, cell_temp = thermals
                led_temp = led_temp or 0
                heatsink_temp = heatsink_temp or 0
                cell_temp = cell_temp or 0
                print(f"Cooling down... LED: {led_temp}°C, Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")
            else:
                print("Cannot read the temperature sensors")
                return False

        print("Temperature back to safe levels. Resuming operation.")
        if previous_light_settings:
            sim.setLEDs(
                r=previous_light_settings['r'],
                g=previous_light_settings['g'],
                b=previous_light_settings['b'],
                uv=previous_light_settings['uv'],
                h=previous_light_settings['h']
            )
        return True

    return True

def check_for_interrupt():

    if supervisor.runtime.serial_bytes_available:
        input_char = sys.stdin.read(1)
        if input_char == '\x03': #Ctrl-C (ASCII 3)
            print("\nCtrl-C detected. Turning off LEDs...")
            sim.setLEDs(0, 0, 0, 0, 0)
            raise KeyboardInterrupt
        else:
            print(f"Ignored input: {repr(input_char)}")