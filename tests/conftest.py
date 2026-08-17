"""Pytest configuration."""

import sys
from unittest.mock import MagicMock

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
    "usb_cdc",
}


for cp_module in CIRCUITPYTHON_MODULES:
    sys.modules.setdefault(cp_module, MagicMock())

sys.modules["micropython"].const = lambda x: x
