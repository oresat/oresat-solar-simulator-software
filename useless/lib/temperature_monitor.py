# temperature_monitor.py

import time

class TemperatureMonitor:
    """
    Handles temperature monitoring and thermal shutdown mechanisms.
    """

    def __init__(self, simulator, thresholds, enable_monitoring=True):
        self.simulator = simulator
        self.thresholds = thresholds
        self.enable_monitoring = enable_monitoring

    def check_temperature(self):
        """
        Checks the temperature readings and handles thermal shutdown if necessary.
        """
        if not self.enable_monitoring:
            return True

        thermals = self.simulator.check_thermals()

        if not thermals:
            print("Cannot read the temperature sensors")
            return False

        led_temp, heatsink_temp, cell_temp = thermals

        # Check if any temperature exceeds the shutdown threshold
        if (
            led_temp > self.thresholds['led_shutdown'] or
            heatsink_temp > self.thresholds['heatsink_shutdown'] or
            cell_temp > self.thresholds['cell_shutdown']
        ):
            previous_light_settings = self.simulator.current_light_settings.copy()
            print("The thermal temperature is too high, turning off the light for safety.")
            self.simulator.set_leds(0, 0, 0, 0, 0)

            # Wait until temperatures drop below resume threshold
            while (
                led_temp > self.thresholds['resume_temp'] or
                heatsink_temp > self.thresholds['resume_temp'] or
                cell_temp > self.thresholds['resume_temp']
            ):
                time.sleep(1)
                thermals = self.simulator.check_thermals()
                if thermals:
                    led_temp, heatsink_temp, cell_temp = thermals
                    print(f"Waiting for temperatures to cool down... LED: {led_temp}°C")
                    print(f"Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")
                else:
                    print("Cannot read the temperature sensors")
                    return False

            print("Temperature is back to safe levels. Resuming operation.")
            self.simulator.set_leds(**previous_light_settings)
            return True

        return True
