import pytest
import supervisor

from solar_simulator import SolarSimulator
from solar_simulator.lib.modes.manual_mode import ManualMode
from solar_simulator.lib.solar_simulator import ThermalSensorError


@pytest.fixture(autouse=True)
def _quiet_console(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the non-blocking input check from reaching for the captured stdin."""
    monkeypatch.setattr(supervisor.runtime, "serial_bytes_available", False)


def test_run_leaves_manual_mode_when_a_thermistor_faults(
    sim: SolarSimulator, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # "1" picks fixed preset mode, then sets its intensity to full.
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")
    sim.check_thermals.side_effect = ThermalSensorError("Thermistor voltage out of range: 0.000V")

    ManualMode(sim).run()

    assert (
        "Thermistor voltage out of range: 0.000V. Exiting Manual Mode." in capsys.readouterr().out
    )
    assert sim.set_leds.call_args_list[-1].args == (0, 0, 0, 0)
    assert sim.mcp.channel_a.value == 0
