from unittest.mock import MagicMock

import pytest

from solar_simulator.lib.modes.basilisk_mode import BasiliskMode


@pytest.fixture
def sim() -> MagicMock:
    """A simulator reporting safe temperatures, so thermal shutdown stays out of the way."""
    sim = MagicMock()
    sim.check_thermals.return_value = [25.0, 25.0, 25.0]
    sim.enable_therm_monitoring = True
    sim.therm_led_shutdown = 100
    sim.therm_heatsink_shutdown = 60
    sim.therm_cell_shutdown = 80
    sim.therm_resume_temp = 45
    sim.current_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
    return sim


def test_apply_line_sets_leds_for_a_valid_intensity(sim: MagicMock) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("100")

    # Assert
    sim.set_leds.assert_called_once_with(v=13859, w=31888, c=20478, h=64284)


def test_apply_line_turns_everything_off_at_zero(sim: MagicMock) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("0")

    # Assert
    sim.set_leds.assert_called_once_with(v=0, w=0, c=0, h=0)


@pytest.mark.parametrize("line", ["", "   ", "abc", "12.5", "-1", "101"])
def test_apply_line_ignores_a_bad_line_without_raising(sim: MagicMock, line: str) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line(line)

    # Assert
    sim.set_leds.assert_not_called()
