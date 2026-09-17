import io
import sys

import pytest

from solar_simulator import SolarSimulator
from solar_simulator.lib import console
from solar_simulator.lib.solar_simulator import ThermalSensorError


def test_check_for_interrupt_turns_off_the_lights_on_ctrl_c(
    sim: SolarSimulator, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(console.supervisor.runtime, "serial_bytes_available", True)
    monkeypatch.setattr(sys, "stdin", io.StringIO("\x03"))

    with pytest.raises(KeyboardInterrupt):
        console.check_for_interrupt(sim)

    sim.set_leds.assert_called_once_with(0, 0, 0, 0)


def test_display_status_reports_a_thermistor_fault(
    sim: SolarSimulator, capsys: pytest.CaptureFixture[str]
) -> None:
    sim.check_thermals.side_effect = ThermalSensorError("Thermistor voltage out of range: 0.000V")

    console.display_status(sim)

    printed = capsys.readouterr().out
    assert "Thermistor voltage out of range: 0.000V" in printed
    assert "VIOLET:0%" in printed
