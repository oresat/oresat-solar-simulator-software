from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from solar_simulator.lib.utils import check_temperature


@pytest.fixture
def sim() -> MagicMock:
    """A simulator lit and thermally safe, with its stock thresholds."""
    sim = MagicMock()
    sim.check_thermals.return_value = [25.0, 25.0, 25.0]
    sim.enable_therm_monitoring = True
    sim.therm_safe = True
    sim.therm_led_shutdown = 100
    sim.therm_heatsink_shutdown = 60
    sim.therm_cell_shutdown = 80
    sim.therm_resume_temp = 45
    sim.current_light_settings = {'v': 100, 'w': 200, 'c': 300, 'h': 400}
    sim.pending_light_settings = {'v': 0, 'w': 0, 'c': 0, 'h': 0}
    return sim


def test_a_cool_panel_may_be_lit(sim: MagicMock) -> None:
    # Act
    lit, thermals = check_temperature(sim)

    # Assert
    assert lit is True
    assert thermals == [25.0, 25.0, 25.0]
    sim.set_leds.assert_not_called()


def test_monitoring_can_be_turned_off(sim: MagicMock) -> None:
    # Arrange
    sim.enable_therm_monitoring = False

    # Act
    lit, thermals = check_temperature(sim)

    # Assert
    assert lit is True
    assert thermals == []
    sim.check_thermals.assert_not_called()


@pytest.mark.parametrize(
    "thermals",
    [
        [120.0, 25.0, 25.0],
        [25.0, 70.0, 25.0],
        [25.0, 25.0, 90.0],
    ],
)
def test_any_channel_over_its_threshold_cuts_the_lamp(
    sim: MagicMock, thermals: list[float]
) -> None:
    # Arrange
    sim.check_thermals.return_value = thermals

    # Act
    lit, reading = check_temperature(sim)

    # Assert
    assert lit is False
    assert sim.therm_safe is False
    assert reading == thermals
    assert sim.pending_light_settings == {'v': 100, 'w': 200, 'c': 300, 'h': 400}
    sim.set_leds.assert_called_once_with(0, 0, 0, 0)


def test_the_call_that_cuts_the_lamp_returns_rather_than_waiting(sim: MagicMock) -> None:
    """The old cooldown loop blocked here until the panel cooled; one call now decides once."""
    # Arrange
    sim.check_thermals.side_effect = [[120.0, 25.0, 25.0], [25.0, 25.0, 25.0]]

    # Act
    lit, _ = check_temperature(sim)

    # Assert
    assert lit is False
    assert sim.check_thermals.call_count == 1


def test_one_channel_still_hot_holds_the_lamp_dark(sim: MagicMock) -> None:
    """Resuming takes all three channels; the cell here is still above the resume point."""
    # Arrange
    sim.therm_safe = False
    sim.check_thermals.return_value = [25.0, 25.0, 50.0]

    # Act
    lit, _ = check_temperature(sim)

    # Assert
    assert lit is False
    assert sim.therm_safe is False
    sim.set_leds.assert_not_called()


def test_a_cooled_panel_resumes_at_the_setpoint_it_was_holding(sim: MagicMock) -> None:
    # Arrange
    sim.therm_safe = False
    sim.pending_light_settings = {'v': 100, 'w': 200, 'c': 300, 'h': 400}
    sim.check_thermals.return_value = [45.0, 40.0, 30.0]

    # Act
    lit, _ = check_temperature(sim)

    # Assert
    assert lit is True
    assert sim.therm_safe is True
    sim.set_leds.assert_called_once_with(v=100, w=200, c=300, h=400)
