"""Test fixtures, config, mocks, and hooks."""

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from solar_simulator import SolarSimulator


@pytest.fixture
def boot_script(monkeypatch: pytest.MonkeyPatch) -> str:
    """Safely prepare sys.path and return the absolute path to boot.py."""
    project_root = Path("./src/solar_simulator").resolve()
    monkeypatch.syspath_prepend(project_root)

    return str(project_root / "boot.py")


@pytest.fixture
def code_script(monkeypatch: pytest.MonkeyPatch) -> str:
    """Fixture that safely prepares sys.path and returns the absolute path to code.py."""
    project_root = Path("./src/solar_simulator").resolve()
    monkeypatch.syspath_prepend(project_root)

    return str(project_root / "code.py")


@pytest.fixture(autouse=True)
def mock_circuitpython() -> None:
    """Inject fake board and pwmio modules before SolarSimulator is imported.

    This runs automatically for every test so you never need to think about
    the hardware imports again.
    """
    fake_board = MagicMock()
    fake_pwmio = MagicMock()

    with patch.dict("sys.modules", {"board": fake_board, "pwmio": fake_pwmio}):
        yield fake_board, fake_pwmio


@pytest.fixture
def solar_simulator(
    mock_circuitpython: tuple[MagicMock, MagicMock]) -> tuple[SolarSimulator, MagicMock]:
    """Fixture providing a fresh SolarSimulator with hardware mocks."""
    _fake_board, fake_pwmio = mock_circuitpython
    fake_pwm_instance = MagicMock()
    fake_pwmio.PWMOut.return_value = fake_pwm_instance

    from solar_simulator import SolarSimulator  # noqa: PLC0415

    sim = SolarSimulator()
    return sim, fake_pwm_instance
