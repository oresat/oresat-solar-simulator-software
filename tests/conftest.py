"""Pytest configuration."""

import sys
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


@pytest.fixture
def sim() -> MagicMock:
    """Build a simulator reporting safe temperatures, so thermal shutdown stays out of the way."""
    sim = MagicMock()
    sim.check_thermals.return_value = [25.0, 25.0, 25.0]
    sim.enable_therm_monitoring = True
    sim.therm_led_shutdown = 100
    sim.therm_heatsink_shutdown = 60
    sim.therm_cell_shutdown = 80
    sim.therm_resume_temp = 45
    sim.current_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
    return sim
