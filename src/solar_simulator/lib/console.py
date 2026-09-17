"""Console reporting and input for the interactive builds.

Only the `complete` build ships this module. Headless mode speaks the Basilisk protocol
on the same serial port, where a status line once a second and a stray-keystroke notice
would be noise between protocol responses.
"""

import sys

import supervisor

from .solar_simulator import SolarSimulator as Sim
from .solar_simulator import ThermalSensorError


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


def check_for_interrupt(sim: Sim) -> None:
    """Listen for keyboard interrupts."""
    if supervisor.runtime.serial_bytes_available:
        input_char = sys.stdin.read(1)

        if input_char == '\x03':  # Ctrl-C (ASCII 3)
            print("\nCtrl-C detected. Turning off LEDs...")
            sim.set_leds(0, 0, 0, 0)
            raise KeyboardInterrupt

        print(f"Ignored input: {repr(input_char)}")  # noqa: RUF010
