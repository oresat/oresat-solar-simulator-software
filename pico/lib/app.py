# lib/app.py

from .utils import input_with_default
from .modes.auto_mode import AutoMode
from .modes.manual_mode import ManualMode
from .modes.basilisk_mode import BasiliskMode

THERM_LED_SHUTDOWN = 100
THERM_HEATSINK_SHUTDOWN = 60
THERM_CELL_SHUTDOWN = 80
THERM_RESUME_TEMP = 45
ENABLE_THERM_MONITORING = True


class SolarSimulatorApp:
    """
    Main application class for the Solar Simulator.
    """

    def __init__(self, sim):
        self.sim = sim
        self.enable_therm_monitoring = "yes"

    def run(self):
        self.setup()
        self.mode_selection()

    def setup(self):
        global ENABLE_THERM_MONITORING, THERM_LED_SHUTDOWN, THERM_HEATSINK_SHUTDOWN, THERM_CELL_SHUTDOWN, THERM_RESUME_TEMP

        # Thermal monitoring setting
        enable_therm_monitoring_input = input_with_default(
            "Would you like to enable thermal monitoring? (yes/no, default is yes): ",
            default_value="yes",
            valid_values=["yes", "no"]
        )
        ENABLE_THERM_MONITORING = enable_therm_monitoring_input == "yes"

        # UV light setting
        enable_uv_input = input_with_default(
            "Would you like to enable the UV light? (yes/no, default is no): ",
            default_value="no",
            valid_values=["yes", "no"]
        )
        self.sim.uv_safety = not (enable_uv_input == "yes")

        THERM_LED_SHUTDOWN = input_with_default(
            "Set LED shutdown temperature (default is 100°C): ",
            default_value=100,
            value_type=int
        )
        THERM_HEATSINK_SHUTDOWN = input_with_default(
            "Set Heatsink shutdown temperature (default is 60°C): ",
            default_value=60,
            value_type=int
        )
        THERM_CELL_SHUTDOWN = input_with_default(
            "Set Cell shutdown temperature (default is 80°C): ",
            default_value=80,
            value_type=int
        )
        THERM_RESUME_TEMP = input_with_default(
            "Set temperature to resume operation (default is 45°C): ",
            default_value=45,
            value_type=int
        )

    def mode_selection(self):
        print("Please choose your mode")
        print("1. Auto Mode")
        print("2. Manual Mode")
        print("3. Basilisk Mode")
        while True:
            mode = input("Your mode (input 1, 2, or 3): ")
            if mode in ["1", "2", "3"]:
                mode = int(mode)
                break
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

        if mode == 1:
            auto_mode = AutoMode(self.sim)
            auto_mode.run()
        elif mode == 2:
            manual_mode = ManualMode(self.sim)
            manual_mode.run()
        elif mode == 3:
            basilisk_mode = BasiliskMode(self.sim)
            basilisk_mode.run()
        else:
            print("Invalid selection, please restart the program and choose 1, 2, or 3.")
