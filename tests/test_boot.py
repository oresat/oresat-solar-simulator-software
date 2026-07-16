"""Tests for the boot.py hardware configuration."""

import runpy
from unittest.mock import MagicMock, patch


def test_boot_enables_usb_cdc(boot_script: str) -> None:
    """Ensure boot.py enables the USB CDC console and data connections."""
    fake_usb_cdc = MagicMock()

    with patch.dict("sys.modules", {"usb_cdc": fake_usb_cdc}):
        runpy.run_path(boot_script, run_name="__main__")

        fake_usb_cdc.enable.assert_called_once_with(console=True, data=True)
