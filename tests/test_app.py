from unittest.mock import MagicMock, patch

import pytest

from solar_simulator.lib.app import SolarSimulatorApp


@pytest.mark.parametrize("build_mode", ["headless", "", "nonsense"])
@patch("solar_simulator.lib.app.BasiliskMode")
def test_run_starts_basilisk_mode_for_any_non_complete_build(
    mock_basilisk_class: MagicMock, build_mode: str
) -> None:
    # Arrange
    sim = MagicMock()
    app = SolarSimulatorApp(sim)

    # Act
    app.run(build_mode)

    # Assert
    mock_basilisk_class.assert_called_once_with(sim)
    mock_basilisk_class.return_value.run.assert_called_once_with()


@patch("solar_simulator.lib.cli.Cli")
def test_run_starts_the_cli_for_the_complete_build(mock_cli_class: MagicMock) -> None:
    # Arrange
    sim = MagicMock()
    app = SolarSimulatorApp(sim)

    # Act
    app.run("complete")

    # Assert
    mock_cli_class.assert_called_once_with(sim)
    mock_cli_class.return_value.run.assert_called_once_with()


def test_run_does_not_import_the_cli_in_headless_mode() -> None:
    """The headless build does not ship cli.mpy, so importing it would crash the device."""
    # Arrange
    app = SolarSimulatorApp(MagicMock())

    # Act / Assert
    with patch("solar_simulator.lib.app.BasiliskMode"), patch.dict("sys.modules", {}, clear=False):
        import sys

        sys.modules.pop("solar_simulator.lib.cli", None)
        app.run("headless")
        assert "solar_simulator.lib.cli" not in sys.modules
