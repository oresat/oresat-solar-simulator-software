"""Utility class for Solar Simulator."""

import time

from .solar_simulator import SolarSimulator as Sim

try:
    from typing import Callable
except ImportError:
    Callable = None


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
        "Violet": violet_intensity,
        "White": white_intensity,
        "Cyan": cyan_intensity,
        "Halogen": halogen_intensity,
    }


def check_temperature(sim: Sim, on_shutdown: "Callable[[], None]" = None) -> bool:
    """Check the temperature, and handle thermal shutdown and resume.

    `on_shutdown` is called once the lights have been turned off and before the cooldown
    wait blocks, so a caller can report the shutdown while it is still news.
    """
    if not sim.enable_therm_monitoring:
        return True

    thermals = sim.check_thermals()
    if not thermals:
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
        sim.set_leds(0, 0, 0, 0)
        if on_shutdown:
            on_shutdown()

        while (
            led_temp > sim.therm_resume_temp
            and heatsink_temp > sim.therm_resume_temp
            and cell_temp > sim.therm_resume_temp
        ):
            time.sleep(1)
            thermals = sim.check_thermals()
            if thermals:
                led_temp, heatsink_temp, cell_temp = thermals
                led_temp = led_temp or 0
                heatsink_temp = heatsink_temp or 0
                cell_temp = cell_temp or 0
            else:
                return False

        if previous_light_settings:
            sim.set_leds(
                v=previous_light_settings['v'],
                w=previous_light_settings['w'],
                c=previous_light_settings['c'],
                h=previous_light_settings['h'],
            )
        return True

    return True
