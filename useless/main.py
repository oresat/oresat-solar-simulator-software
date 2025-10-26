# main.py

from lib.solar_simulator import SolarSimulator
from lib.temperature_monitor import TemperatureMonitor
from lib.input_handler import InputHandler
from lib.light_patterns import LightPatterns
from lib.utils import input_with_default

def main():
    # Initialize SolarSimulator
    sim = SolarSimulator(verbose=0)
    sim.set_leds(0, 0, 0, 0, 0)  # Ensure all LEDs are turned off initially

    # Temperature thresholds
    thresholds = {
        'led_shutdown': 100,
        'heatsink_shutdown': 60,
        'cell_shutdown': 80,
        'resume_temp': 45
    }

    # Thermal monitoring setting
    enable_therm_monitoring_input = input_with_default(
        "Would you like to enable thermal monitoring? (yes/no, default is yes): ",
        default_value="yes",
        valid_values=["yes", "no"]
    )
    enable_therm_monitoring = enable_therm_monitoring_input == "yes"

    # UV light setting
    enable_uv_input = input_with_default(
        "Would you like to enable the UV light? (yes/no, default is no): ",
        default_value="no",
        valid_values=["yes", "no"]
    )
    sim.uv_safety = not (enable_uv_input == "yes")

    # Temperature thresholds setting
    thresholds['led_shutdown'] = input_with_default(
        "Set LED shutdown temperature (default is 100°C): ",
        default_value=100,
        value_type=int
    )
    thresholds['heatsink_shutdown'] = input_with_default(
        "Set Heatsink shutdown temperature (default is 60°C): ",
        default_value=60,
        value_type=int
    )
    thresholds['cell_shutdown'] = input_with_default(
        "Set Cell shutdown temperature (default is 80°C): ",
        default_value=80,
        value_type=int
    )
    thresholds['resume_temp'] = input_with_default(
        "Set temperature to resume operation (default is 45°C): ",
        default_value=45,
        value_type=int
    )

    # Initialize TemperatureMonitor and InputHandler
    temp_monitor = TemperatureMonitor(sim, thresholds, enable_monitoring=enable_therm_monitoring)
    input_handler = InputHandler(sim)

    # Initialize LightPatterns
    patterns = LightPatterns(sim, temp_monitor, input_handler)

    # Mode selection
    print("Please choose your mode")
    print("1. Auto Mode")
    print("2. Manual Mode")
    print("3. Basilisk Mode")
    while True:
        mode = input("Your mode (input 1, 2, or 3): ")
        if mode in ["1", "2", "3"]:
            break
        else:
            print("Invalid input. Please enter 1, 2, or 3.")

    if mode == '1':
        patterns.auto_mode()
    elif mode == '2':
        patterns.manual_mode()
    elif mode == '3':
        patterns.basilisk_mode()
    else:
        print("Invalid selection, please restart the program and choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
