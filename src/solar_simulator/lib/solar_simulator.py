"""The SolarSimulator module."""

import board
from pwmio import PWMOut


class SolarSimulator:
    """Simulates solar intensity through light device brightness.

    This class abstracts hardware control for the solar simulator lab device.
    """

    def __init__(self, pwm_freq: int = 5000) -> None:
        """Initialize the SolarSimulator."""
        self.PWM_FREQ = pwm_freq
        self.hal = PWMOut(board.GP28, frequency=self.PWM_FREQ, duty_cycle=0)
        self.light_settings = {
            'h': 0,
        }


    def set_lights(self, h: int = 0) -> None:
        """Set the light brightness levels and record the light configuration."""
        self.hal.duty_cycle = h
        self.light_settings = {
            'h': h,
        }
