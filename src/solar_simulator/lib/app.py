"""Solar Simulator Application."""

from .modes.auto_mode import AutoMode
from .modes.basilisk_mode import BasiliskMode
from .modes.manual_mode import ManualMode
from .solar_simulator import SolarSimulator as Sim
from .utils import input_with_default


class SolarSimulatorApp:
    """Main application class for the Solar Simulator."""

    def __init__(self, sim: Sim) -> None:
        """Initialize Solar Simulator App."""
        self.sim = sim


    def run(self) -> None:
        """Run the Solar Simulator App."""
        self.mode_selection()


    def setup(self) -> None:
        """Set up the cli menu options."""
        default_settings_summary = (
                "\nDefault settings are:\n"
                "  - Thermal Monitoring: " + ("Enabled" if self.sim.enable_therm_monitoring else "Disabled") + "\n" +  # noqa: E501
                "  - LED Shutdown Temperature: " + str(self.sim.therm_led_shutdown) + "°C\n" +
                "  - Heatsink Shutdown Temperature: " + str(self.sim.therm_heatsink_shutdown) + "°C\n" +  # noqa: E501
                "  - Cell Shutdown Temperature: " + str(self.sim.therm_cell_shutdown) + "°C\n" +
                "  - Resume Operation Temperature: " + str(self.sim.therm_resume_temp) + "°C\n"
        )

        change_settings = input_with_default(
            f"Would you like to change the default settings? (yes/no, default is no): {default_settings_summary}",  # noqa: E501
            default_value="no",
            valid_values=["yes", "no"]
        )

        if change_settings == "yes":
            # Thermal monitoring setting
            enable_therm_monitoring_input = input_with_default(
                "Would you like to enable thermal monitoring? (yes/no, default is yes): ",
                default_value="yes",
                valid_values=["yes", "no"]
            )
            self.sim.enable_therm_monitoring = enable_therm_monitoring_input == "yes"

            # Thermal shutdown temperatures
            self.sim.therm_led_shutdown = input_with_default(
                "Set LED shutdown temperature (default is 100°C): ",
                default_value=100,
                value_type=int
            )
            self.sim.therm_heatsink_shutdown = input_with_default(
                "Set Heatsink shutdown temperature (default is 60°C): ",
                default_value=60,
                value_type=int
            )
            self.sim.therm_cell_shutdown = input_with_default(
                "Set Cell shutdown temperature (default is 80°C): ",
                default_value=80,
                value_type=int
            )
            self.sim.therm_resume_temp = input_with_default(
                "Set temperature to resume operation (default is 45°C): ",
                default_value=45,
                value_type=int
            )
        else:
            print("Using default settings. No changes were made.")

    def mode_selection(self) -> None:
        """Mode selection menu."""
        print("Please choose your mode")
        print("1. Auto Mode")
        print("2. Manual Mode")
        print("3. Basilisk Mode")
        print("4. Thermal setup, if you need")

        while True:
            mode = input("Your mode (input 1, 2, 3 or 4 if you need change default): ")

            if mode in ["1", "2", "3","4"]:
                mode = int(mode)
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

            if mode == 1:
                auto_mode = AutoMode(self.sim)
                auto_mode.run()
                break

            if mode == 2:
                manual_mode = ManualMode(self.sim)
                manual_mode.run()
                break

            if mode == 3:
                basilisk_mode = BasiliskMode(self.sim)
                basilisk_mode.run()
                break

            if mode == 4:
                self.setup()
                print("Thermal setup completed. Returning to mode selection.\n")
                continue
        else:
            print("Invalid selection, please restart the program and choose 1, 2, or 3.")
