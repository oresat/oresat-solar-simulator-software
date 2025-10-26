# utils.py

def calculate_light_intensity(factor):
    """
    Calculate the light intensity values for 5 types of lights.

    :param factor: Scaling factor between 0 and 1
    :return: Dictionary with intensities for Red, Green, Blue, Halogen, and UV
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

def input_with_default(prompt, default_value, valid_values=None, value_type=str):
    """
    Prompts the user for input with a default value.

    :param prompt: Prompt message
    :param default_value: Default value if user input is empty
    :param valid_values: List of valid values
    :param value_type: Expected type of the input
    :return: User input value
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

def display_status(simulator):
    """
    Displays the current status of temperatures and light intensities.

    :param simulator: SolarSimulator instance
    """
    try:
        thermals = simulator.check_thermals()
        if thermals:
            led_temp, heatsink_temp, cell_temp = thermals
            temp_info = "LED: {:.1f}°C, Heatsink: {:.1f}°C, Cell: {:.1f}°C".format(led_temp, heatsink_temp, cell_temp)
        else:
            temp_info = "Cannot read temperature data"
    except (ValueError, TypeError):
        temp_info = "Temperature data unavailable"

    try:
        light_settings = simulator.current_light_settings
        light_info = f"RED: {light_settings['r'] // 655}%, GRN: {light_settings['g'] // 655}%, " \
                     f"BLU: {light_settings['b'] // 655}%, UV: {(light_settings['uv'] // 655) if not simulator.uv_safety else 0}%, " \
                     f"HAL: {light_settings['h'] // 655}%"
    except Exception:
        light_info = "Light data unavailable"

    print(f"\r{temp_info} | {light_info}", end="\n")

