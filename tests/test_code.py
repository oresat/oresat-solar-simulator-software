import code
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.parametrize("build_mode", ["headless", "complete"])
@patch("code.SolarSimulatorApp")
@patch("code.SolarSimulator")
def test_main_initializes_leds_off_and_runs_app(
    mock_sim_class: MagicMock, mock_app_class: MagicMock, build_mode: str
) -> None:
    # Arrange
    mock_sim = mock_sim_class.return_value
    mock_app = mock_app_class.return_value

    # Act
    with patch("code.build_mode", build_mode):
        code.main()

    # Assert
    mock_sim_class.assert_called_once_with()
    mock_sim.set_leds.assert_called_once_with(0, 0, 0, 0)

    mock_app_class.assert_called_once_with(mock_sim)
    mock_app.run.assert_called_once_with(build_mode)
