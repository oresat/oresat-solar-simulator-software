from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
import supervisor

from solar_simulator.lib.modes.basilisk_mode import BasiliskMode

if TYPE_CHECKING:
    from collections.abc import Iterator

COOL = " led=25.0 heatsink=25.0 cell=25.0"
"""The reading the `sim` fixture reports, as it appears on the wire."""


class FakeClock:
    """A hand-advanced monotonic clock, so a five-second silence costs no wall time."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


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
    sim.therm_safe = True
    sim.current_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
    sim.pending_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
    return sim


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def quiet_port() -> Iterator[None]:
    """A serial port with nothing waiting on it, so `tick` reaches the watchdog."""
    original = supervisor.runtime.serial_bytes_available
    supervisor.runtime.serial_bytes_available = 0
    yield
    supervisor.runtime.serial_bytes_available = original


def test_apply_line_sets_leds_for_a_valid_intensity(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("100")

    # Assert
    sim.set_leds.assert_called_once_with(v=13859, w=31888, c=20478, h=64284)
    assert capsys.readouterr().out == f"OK 100{COOL}\n"


def test_apply_line_turns_everything_off_at_zero(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("0")

    # Assert
    sim.set_leds.assert_called_once_with(v=0, w=0, c=0, h=0)
    assert capsys.readouterr().out == f"OK 0{COOL}\n"


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
    """A rejected line never reached the sensors, so it answers without a reading."""
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
    assert capsys.readouterr().out == f"OK 50{COOL}\n"


def test_apply_line_reports_the_reading_its_answer_was_decided_on(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """The numbers on the wire are the ones the thermal decision used, not a later read."""
    # Arrange
    sim.check_thermals.return_value = [31.25, 28.44, 27.9]
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("50")

    # Assert
    assert capsys.readouterr().out == "OK 50 led=31.2 heatsink=28.4 cell=27.9\n"
    assert sim.check_thermals.call_count == 1


def test_apply_line_omits_the_reading_when_monitoring_is_off(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    sim.enable_therm_monitoring = False
    mode = BasiliskMode(sim)

    # Act
    mode.apply_line("50")

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
    assert capsys.readouterr().out == "WARN THERMAL 50 led=120.0 heatsink=25.0 cell=25.0\n"


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
    assert capsys.readouterr().out == f"OK 50{COOL}\n"


def test_apply_line_holds_the_value_without_relighting_while_the_panel_cools(
    sim: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """A held value must not reach the lamp, or every line would pulse it back on."""
    # Arrange
    sim.check_thermals.side_effect = [[120.0, 25.0, 25.0], [120.0, 25.0, 25.0]]
    mode = BasiliskMode(sim)
    mode.apply_line("50")
    sim.set_leds.reset_mock()
    capsys.readouterr()

    # Act
    mode.apply_line("75")

    # Assert
    sim.set_leds.assert_not_called()
    assert sim.pending_light_settings == {'v': 14106, 'w': 26591, 'c': 18797, 'h': 49687}
    assert capsys.readouterr().out == "WARN THERMAL 75 led=120.0 heatsink=25.0 cell=25.0\n"


@pytest.mark.usefixtures("quiet_port")
def test_a_host_that_goes_quiet_loses_the_lamp(sim: MagicMock, clock: FakeClock) -> None:
    # Arrange
    mode = BasiliskMode(sim, clock=clock)

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S + 0.1)
    mode.tick()

    # Assert
    sim.set_leds.assert_called_once_with(0, 0, 0, 0)


@pytest.mark.usefixtures("quiet_port")
def test_a_host_still_inside_the_timeout_keeps_the_lamp(sim: MagicMock, clock: FakeClock) -> None:
    # Arrange
    mode = BasiliskMode(sim, clock=clock)

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S - 0.1)
    mode.tick()

    # Assert
    sim.set_leds.assert_not_called()


@pytest.mark.usefixtures("quiet_port")
def test_the_watchdog_safes_the_lamp_once_rather_than_every_tick(
    sim: MagicMock, clock: FakeClock
) -> None:
    """A board left alone overnight must not keep writing to the DAC forever."""
    # Arrange
    mode = BasiliskMode(sim, clock=clock)
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S + 0.1)
    mode.tick()
    sim.set_leds.reset_mock()

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S * 10)
    mode.tick()

    # Assert
    sim.set_leds.assert_not_called()


@pytest.mark.usefixtures("quiet_port")
def test_the_watchdog_drops_a_setpoint_held_for_a_cooling_panel(
    sim: MagicMock, clock: FakeClock
) -> None:
    """Left pending, it would relight the lamp the moment the panel cooled, host or no host."""
    # Arrange
    sim.therm_safe = False
    sim.pending_light_settings = {'v': 100, 'w': 200, 'c': 300, 'h': 400}
    mode = BasiliskMode(sim, clock=clock)

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S + 0.1)
    mode.tick()

    # Assert
    assert sim.pending_light_settings == {'v': 0, 'w': 0, 'c': 0, 'h': 0}


@pytest.mark.usefixtures("quiet_port")
def test_a_returning_host_rearms_the_watchdog(
    sim: MagicMock, clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim, clock=clock)
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S + 0.1)
    mode.tick()
    mode.receive("50")
    sim.set_leds.reset_mock()
    capsys.readouterr()

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S + 0.1)
    mode.tick()

    # Assert
    sim.set_leds.assert_called_once_with(0, 0, 0, 0)


@pytest.mark.usefixtures("quiet_port")
def test_a_line_the_protocol_rejects_still_proves_the_host_is_alive(
    sim: MagicMock, clock: FakeClock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    mode = BasiliskMode(sim, clock=clock)

    # Act
    clock.advance(BasiliskMode.QUIET_TIMEOUT_S - 0.1)
    mode.receive("abc")
    clock.advance(0.2)
    mode.tick()

    # Assert
    sim.set_leds.assert_not_called()
    assert capsys.readouterr().out == "ERR PARSE invalid intensity value received: abc\n"
