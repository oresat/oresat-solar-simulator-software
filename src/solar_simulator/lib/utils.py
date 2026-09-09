"""Utility class for Solar Simulator."""

from .solar_simulator import SolarSimulator as Sim


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


def check_temperature(sim: Sim) -> bool:
    """Advance the thermal state one step and say whether the lamp may be lit.

    One call reads the sensors once and decides once; it never waits for the panel to
    cool. A caller that wants to wait calls again, and stays free to do something else in
    between -- answer the host, abort the run -- instead of disappearing for minutes
    (ADR-0007 in `brysat-flathils`).

    The lamp is cut when any channel passes its shutdown threshold, and the setpoint it
    was carrying is held in `sim.pending_light_settings` until every channel is back under
    `sim.therm_resume_temp`. Resuming takes all three, because one cool channel does not
    make the panel safe.

    Says nothing on the console: the only caller answers the host on the protocol stream,
    which no other output may share.
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

    if sim.therm_safe:
        if (
            led_temp > sim.therm_led_shutdown
            or heatsink_temp > sim.therm_heatsink_shutdown
            or cell_temp > sim.therm_cell_shutdown
        ):
            sim.pending_light_settings = sim.current_light_settings
            sim.set_leds(0, 0, 0, 0)
            sim.therm_safe = False
            return False
        return True

    if max(led_temp, heatsink_temp, cell_temp) > sim.therm_resume_temp:
        return False

    sim.therm_safe = True
    pending = sim.pending_light_settings
    sim.set_leds(v=pending['v'], w=pending['w'], c=pending['c'], h=pending['h'])
    return True
