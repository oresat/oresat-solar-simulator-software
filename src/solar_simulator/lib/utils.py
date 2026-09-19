"""Utility functions for Solar Simulator."""

import time

from .solar_simulator import SolarSimulator as Sim
from .solar_simulator import ThermalSensorError


def calculate_light_intensity(factor: float) -> dict:
    """Calculate the light intensity values for 5 types of lights."""
    if not (0 <= factor <= 1):
        raise ValueError("Scaling factor must be between 0 and 1.")

    if factor == 0:
        violet_intensity = 0
        white_intensity = 0
        cyan_intensity = 0
        halogen_intensity = 0
    elif 0 < factor <= 1:
        violet_intensity = -1.5066 * factor + 22.6663
        white_intensity = 32.3521 * factor + 16.3331
        cyan_intensity = 10.2647 * factor + 20.9998
        halogen_intensity = 89.1446 * factor + 9.0003

    return {
        "v": int(violet_intensity * 655),
        "w": int(white_intensity * 655),
        "c": int(cyan_intensity * 655),
        "h": int(halogen_intensity * 655),
    }


def display_status(sim: Sim) -> None:
    """Display the current thermal and light status."""
    try:
        thermals = sim.check_thermals()

        if thermals:
            led_temp, heatsink_temp, cell_temp = thermals
            temp_info = (
                f"LED: {led_temp:.1f}°C, Heatsink: {heatsink_temp:.1f}°C, Cell: {cell_temp:.1f}°C"
            )
        else:
            temp_info = "Cannot read temperature data"
    except Exception:  # noqa: BLE001
        temp_info = "Temperature data unavailable"

    current_settings = sim.current_light_settings
    try:
        light_info = f"VIOLET:{current_settings['v'] // 655}% WHITE:{current_settings['w'] // 655}% CYAN:{current_settings['c'] // 655}%  HAL:{current_settings['h'] // 655}%"  # noqa: E501
    except Exception:  # noqa: BLE001
        light_info = "Light data unavailable"

    print(f"{temp_info} | {light_info}", end="\n")


def read_temperatures(sim: Sim) -> tuple:
    """Return the LED, heatsink, and cell temperatures in Celsius."""
    thermals = sim.check_thermals()
    if not thermals:
        raise ThermalSensorError("Cannot read the temperature sensors")

    led_temp, heatsink_temp, cell_temp = thermals

    if not all(led_temp, heatsink_temp, cell_temp):
        raise ThermalSensorError("Invalid temperature sensor reading")

    return (led_temp, heatsink_temp, cell_temp)


def is_within_thermal_limits(sim: Sim, temperatures: tuple) -> bool:
    """Return whether every temperature is at or below its own shutdown limit."""
    limits = (sim.therm_led_shutdown, sim.therm_heatsink_shutdown, sim.therm_cell_shutdown)
    return all(temp <= limit for temp, limit in zip(temperatures, limits))


def has_cooled_down(sim: Sim, temperatures: tuple) -> bool:
    """Return whether every temperature is back at or below the resume limit."""
    return all(temp <= sim.therm_resume_temp for temp in temperatures)


def enforce_thermal_limits(sim: Sim) -> bool:
    """Read the temperatures and change the state of the Solar Sim accordingly."""
    if not sim.enable_therm_monitoring:
        return False

    temperatures = read_temperatures(sim)
    if is_within_thermal_limits(sim, temperatures):
        return False

    previous_light_settings = sim.current_light_settings
    sim.set_leds(0, 0, 0, 0)
    print("Temperature too high! Turning off lights for safety.")

    while not has_cooled_down(sim, temperatures):
        time.sleep(1)
        temperatures = read_temperatures(sim)
        led_temp, heatsink_temp, cell_temp = temperatures
        print("Cooling down ...")
        print(f"LED: {led_temp}°C, Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")

    print("Temperature back to safe levels. Resuming operation.")
    if previous_light_settings:
        sim.set_leds(**previous_light_settings)

    return True
