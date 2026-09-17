"""Pytest configuration."""

import sys
import time
from unittest.mock import MagicMock

import pytest

CIRCUITPYTHON_MODULES = {
    "adafruit_ads1x15",
    "adafruit_ads1x15.ads1015",
    "adafruit_ads1x15.analog_in",
    "adafruit_mcp4728",
    "board",
    "busio",
    "micropython",
    "pdb",
    "pwmio",
    "supervisor",
    "ulab",
}


for cp_module in CIRCUITPYTHON_MODULES:
    sys.modules.setdefault(cp_module, MagicMock())

sys.modules["micropython"].const = lambda x: x

# Importable only once the stand-ins above are in place, since the simulator reaches for
# the board's I2C, ADC, DAC, and PWM the moment it is constructed.
from solar_simulator import SolarSimulator  # noqa: E402


@pytest.fixture
def sim() -> SolarSimulator:
    """Build a simulator whose sensors read safe, so thermal shutdown stays out of the way.

    It is the real class, so the thresholds are the real defaults and the light bookkeeping
    is the real bookkeeping. Only the two edges a test needs to reach are instrumented:
    the thermistors, which have no hardware to read, and set_leds, which tests assert on.
    """
    sim = SolarSimulator()
    sim.check_thermals = MagicMock(return_value=[25.0, 25.0, 25.0])
    sim.set_leds = MagicMock(wraps=sim.set_leds)

    return sim


@pytest.fixture(autouse=True)
def _no_cooldown_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the thermal cooldown poll without waiting a second between readings."""
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
