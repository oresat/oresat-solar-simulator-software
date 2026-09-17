"""Thermal supervision for the solar simulator.

The simulator decides whether it is too hot, using thresholds it carries and sensors it
owns. This module acts on that decision, which means blocking for as long as the
cooldown takes and narrating it to somebody. Neither belongs in a hardware abstraction.
"""

import time

from .solar_simulator import SolarSimulator as Sim

try:
    from typing import Callable
except ImportError:
    Callable = None


def enforce_thermal_limits(sim: Sim, writer: "Callable[..., None]" = print) -> bool:
    """Hold the lights off until the simulator is back within its thermal limits.

    Return whether a shutdown happened:
        - True once the lights have been turned off, waited out, and restored.
        - False when nothing needed doing.
        - False when monitoring is off, since nothing was measured.

    Progress messages go to `writer`. Raise ThermalSensorError when the thermistors
    cannot be read.
    """
    if not sim.in_thermal_shutdown():
        return False

    sim.blank()
    writer("Temperature too high! Turning off lights for safety.")

    while sim.in_thermal_shutdown():
        time.sleep(1)
        led_temp, heatsink_temp, cell_temp = sim.check_thermals()
        writer("Cooling down ...")
        writer(f"LED: {led_temp}°C, Heatsink: {heatsink_temp}°C, Cell: {cell_temp}°C")

    writer("Temperature back to safe levels. Resuming operation.")
    sim.restore()

    return True
