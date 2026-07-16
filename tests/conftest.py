"""Test fixtures, config, mocks, and hooks."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_circuitpython():
    """Inject fake board and pwmio modules before SolarSimulator is imported.

    This runs automatically for every test so you never need to think about
    the hardware imports again.
    """
    fake_board = MagicMock()
    fake_pwmio = MagicMock()

    with patch.dict("sys.modules", {"board": fake_board, "pwmio": fake_pwmio}):
        yield fake_board, fake_pwmio


@pytest.fixture
def solar_simulator(mock_circuitpython):
    """Fixture providing a fresh SolarSimulator with hardware mocks."""
    fake_board, fake_pwmio = mock_circuitpython
    fake_pwm_instance = MagicMock()
    fake_pwmio.PWMOut.return_value = fake_pwm_instance

    from solar_simulator import SolarSimulator

    sim = SolarSimulator()
    return sim, fake_pwm_instance
