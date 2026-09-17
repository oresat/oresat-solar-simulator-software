import io
import sys
from unittest.mock import MagicMock

import pytest

from solar_simulator.lib import utils


def test_enforce_thermal_limits_waits_for_every_sensor_to_cool(sim: MagicMock) -> None:
    # The LED runs hot on its own; the heatsink and cell are under the resume limit
    # from the first reading, so a check that needs all three to be hot never waits.
    sim.check_thermals.side_effect = [
        [120.0, 25.0, 25.0],
        [90.0, 25.0, 25.0],
        [40.0, 25.0, 25.0],
    ]

    utils.enforce_thermal_limits(sim, writer=lambda _message: None)

    assert sim.check_thermals.call_count == 3


def test_check_for_interrupt_turns_off_the_lights_on_ctrl_c(
    sim: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(utils.supervisor.runtime, "serial_bytes_available", True)
    monkeypatch.setattr(sys, "stdin", io.StringIO("\x03"))

    with pytest.raises(KeyboardInterrupt):
        utils.check_for_interrupt(sim)

    sim.set_leds.assert_called_once_with(0, 0, 0, 0)


def test_enforce_thermal_limits_raises_when_the_sensors_cannot_be_read(sim: MagicMock) -> None:
    sim.check_thermals.return_value = []

    with pytest.raises(utils.ThermalSensorError):
        utils.enforce_thermal_limits(sim, writer=lambda _message: None)
