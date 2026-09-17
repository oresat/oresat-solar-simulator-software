from unittest.mock import MagicMock

import pytest

from solar_simulator.lib.modes.basilisk_mode import BasiliskMode


@pytest.fixture
def mode(sim: MagicMock) -> BasiliskMode:
    """Basilisk mode driving the stub simulator."""
    return BasiliskMode(sim)


@pytest.mark.parametrize(
    ("line", "settings"),
    [
        ("100", {'v': 13859, 'w': 31888, 'c': 20478, 'h': 64284}),
        ("0", {'v': 0, 'w': 0, 'c': 0, 'h': 0}),
    ],
)
def test_apply_line_sets_leds_for_a_valid_intensity(
    mode: BasiliskMode,
    sim: MagicMock,
    capsys: pytest.CaptureFixture[str],
    line: str,
    settings: dict,
) -> None:
    mode.apply_line(line)

    sim.set_leds.assert_called_once_with(**settings)
    assert capsys.readouterr().out == f"OK {line}\n"


@pytest.mark.parametrize(
    ("line", "response"),
    [
        ("", "ERR EMPTY no intensity value received"),
        ("abc", "ERR PARSE invalid intensity value received: abc"),
        ("12.5", "ERR PARSE invalid intensity value received: 12.5"),
        ("-1", "ERR RANGE invalid intensity value received: -1"),
        ("101", "ERR RANGE invalid intensity value received: 101"),
    ],
)
def test_apply_line_reports_a_bad_line(
    mode: BasiliskMode, sim: MagicMock, capsys: pytest.CaptureFixture[str], line: str, response: str
) -> None:
    mode.apply_line(line)

    sim.set_leds.assert_not_called()
    assert capsys.readouterr().out == f"{response}\n"


def test_apply_line_warns_while_hot_then_acknowledges_once_cooled(
    mode: BasiliskMode, sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    sim.check_thermals.side_effect = [[120.0, 25.0, 25.0], [25.0, 25.0, 25.0], [25.0, 25.0, 25.0]]

    mode.apply_line("50")

    assert capsys.readouterr().out == "WARN THERMAL temperature too high, lights off for safety\n"

    mode.apply_line("50")

    assert capsys.readouterr().out == "OK 50\n"


def test_apply_line_reports_a_thermal_sensor_fault(
    mode: BasiliskMode, sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    sim.check_thermals.return_value = []

    mode.apply_line("50")

    assert capsys.readouterr().out == "ERR THERMAL Cannot read the temperature sensors\n"
    assert sim.set_leds.call_args_list[-1].args == (0, 0, 0, 0)
