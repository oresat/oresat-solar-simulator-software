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


def test_apply_line_sets_leds_for_a_valid_intensity(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("100")

    # Assert
    sim.set_leds.assert_called_once_with(v=13859, w=31888, c=20478, h=64284)
    assert capsys.readouterr().out == "OK 100\n"


def test_apply_line_turns_everything_off_at_zero(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("0")

    # Assert
    sim.set_leds.assert_called_once_with(v=0, w=0, c=0, h=0)
    assert capsys.readouterr().out == "OK 0\n"


@pytest.mark.parametrize(
    ("line", "response"),
    [
        ("", "ERR EMPTY no intensity value received"),
        ("   ", "ERR EMPTY no intensity value received"),
        ("abc", "ERR PARSE invalid intensity value received: abc"),
        ("12.5", "ERR PARSE invalid intensity value received: 12.5"),
        ("-1", "ERR RANGE invalid intensity value received: -1"),
        ("101", "ERR RANGE invalid intensity value received: 101"),
    ],
)
def test_apply_line_reports_a_bad_line(
    sim: MagicMock, capsys: pytest.CaptureFixture[str], line: str, response: str
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line(line)

    # Assert
    sim.set_leds.assert_not_called()
    assert capsys.readouterr().out == f"{response}\n"


def test_apply_line_scrubs_stray_bytes_around_a_value(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("\x0050\r")

    # Assert
    assert capsys.readouterr().out == "OK 50\n"


def test_apply_line_warns_during_thermal_shutdown(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """The setpoint is pending, not applied, so `OK` would hide the divergence."""
    # Arrange
    sim.check_thermals.side_effect = [[120.0, 25.0, 25.0], [25.0, 25.0, 25.0]]
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("50")

    # Assert
    assert capsys.readouterr().out == "WARN THERMAL temperature too high, lights off for safety\n"


def test_apply_line_acknowledges_again_once_the_panel_has_cooled(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    sim.check_thermals.side_effect = [[120.0, 25.0, 25.0], [25.0, 25.0, 25.0], [25.0, 25.0, 25.0]]
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("50")
    capsys.readouterr()
    mode.apply_line("50")

    # Assert
    assert capsys.readouterr().out == "OK 50\n"
