"""Utility class for Solar Simulator."""

import sys
import time

import supervisor

from .solar_simulator import SolarSimulator as Sim
from .solar_simulator import ThermalSensorError

try:
    from typing import Callable
except ImportError:
    Callable = None


def calculate_light_intensity(factor: float) -> dict:
    """Return the `set_leds` settings for an intensity factor from 0 to 1."""
    if not (0 <= factor <= 1):
        raise ValueError("Scaling factor must be between 0 and 1.")

    if factor == 0:
        violet_intensity = 0
        white_intensity = 0
        cyan_intensity = 0
        halogen_intensity = 0
    else:
        violet_intensity = -1.5066 * factor + 22.6663
        white_intensity = 32.3521 * factor + 16.3331
        cyan_intensity = 10.2647 * factor + 20.9998
        halogen_intensity = 89.1446 * factor + 9.0003

    return {
        'v': int(violet_intensity * 655),
        'w': int(white_intensity * 655),
        'c': int(cyan_intensity * 655),
        'h': int(halogen_intensity * 655),
    }


def display_status(sim: Sim) -> None:
    """Display the current thermal and light status."""
    try:
        led_temp, heatsink_temp, cell_temp = sim.check_thermals()
        temp_info = (
            f"LED: {led_temp:.1f}°C, Heatsink: {heatsink_temp:.1f}°C, Cell: {cell_temp:.1f}°C"
        )
    except ThermalSensorError as error:
        temp_info = str(error)

    current_settings = sim.current_light_settings
    light_info = f"VIOLET:{current_settings['v'] // 655}% WHITE:{current_settings['w'] // 655}% CYAN:{current_settings['c'] // 655}%  HAL:{current_settings['h'] // 655}%"  # noqa: E501

    print(f"{temp_info} | {light_info}", end="\n")


def enforce_thermal_limits(sim: Sim, writer: "Callable[..., None]" = print) -> bool:
    """Hold the lights off until the simulator is back within its thermal limits.

    Return whether a shutdown happened:
        - True once the lights have been turned off, waited out, and restored.
        - False when nothing needed doing.
        - False when monitoring is off, since nothing was measured.

    Progress messages go to `writer`. Raise ThermalSensorError when the thermistors
    cannot be read.
    """
    if not sim.enable_therm_monitoring:
        return False

    temperatures = sim.check_thermals()
    if sim.is_within_shutdown_limits(temperatures):
        return False

    sim.blank()
    writer("Temperature too high! Turning off lights for safety.")

    while not sim.is_within_resume_limit(temperatures):
        time.sleep(1)
        temperatures = sim.check_thermals()
        led_temp, heatsink_temp, cell_temp = temperatures
        writer("Cooling down ...")
        writer(f"LED: {led_temp}°C, Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")

    writer("Temperature back to safe levels. Resuming operation.")
    sim.restore()

    return True


def check_for_interrupt(sim: Sim) -> None:
    """Listen for keyboard interrupts."""
    if supervisor.runtime.serial_bytes_available:
        input_char = sys.stdin.read(1)

        if input_char == '\x03':  # Ctrl-C (ASCII 3)
            print("\nCtrl-C detected. Turning off LEDs...")
            sim.set_leds(0, 0, 0, 0)
            raise KeyboardInterrupt

        print(f"Ignored input: {repr(input_char)}")  # noqa: RUF010
