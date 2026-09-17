"""Utility class for Solar Simulator."""


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
