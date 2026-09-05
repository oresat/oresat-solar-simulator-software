"""Utility class for Solar Simulator."""

import sys
import time

import supervisor

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


def check_temperature(
    sim: Sim,
    writer: "Callable[..., None]" = print,
    on_shutdown: "Callable[[], None]" = None,
) -> bool:
    """Check the temperature, and handle thermal shutdown and resume.

    Progress messages go to `writer`. `on_shutdown` is called once the lights have been
    turned off and before the cooldown wait blocks, so a caller can report the shutdown
    while it is still news.
    """
    if not sim.enable_therm_monitoring:
        return True

    thermals = sim.check_thermals()
    if not thermals:
        writer("Cannot read the temperature sensors")
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
        writer("Temperature too high! Turning off lights for safety.")
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
                writer("Cooling down ...")
                writer(f"LED: {led_temp}°C, Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")
            else:
                writer("Cannot read the temperature sensors")
                return False

        writer("Temperature back to safe levels. Resuming operation.")
        if previous_light_settings:
            sim.set_leds(
                v=previous_light_settings['v'],
                w=previous_light_settings['w'],
                c=previous_light_settings['c'],
                h=previous_light_settings['h'],
            )
        return True

    return True


def check_for_interrupt() -> None:
    """Listen for keyboard interrupts."""
    if supervisor.runtime.serial_bytes_available:
        input_char = sys.stdin.read(1)

        if input_char == '\x03':  # Ctrl-C (ASCII 3)
            print("\nCtrl-C detected. Turning off LEDs...")
            Sim.set_leds(0, 0, 0, 0)
            raise KeyboardInterrupt

        print(f"Ignored input: {repr(input_char)}")  # noqa: RUF010
