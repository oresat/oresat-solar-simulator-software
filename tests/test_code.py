"""Tests for the code.py entrypoint."""

import runpy
from unittest.mock import patch


def test_main_initializes_solar_simulator(code_script: str) -> None:
    """Ensure calling main() creates an instance of SolarSimulator."""
    with patch("lib.solar_simulator.SolarSimulator") as mock_simulator_class:
        module_globals = runpy.run_path(code_script, run_name="testing_module")
        module_globals["main"]()

        mock_simulator_class.assert_called_once()
