import pytest

from solar_simulator import SolarSimulator
from solar_simulator.lib.solar_simulator import ThermalSensorError


def test_set_leds_updates_state() -> None:
    sim = SolarSimulator()

    sim.set_leds(v=1000, w=2000, c=3000, h=4000)

    assert sim.current_light_settings == {'v': 1000, 'w': 2000, 'c': 3000, 'h': 4000}
    assert sim.mcp.channel_a.value == 1000
    assert sim.mcp.channel_b.value == 2000
    assert sim.mcp.channel_c.value == 3000
    assert sim.hal.duty_cycle == 4000


@pytest.mark.parametrize(
    "v_adc",
    [
        pytest.param(0.0, id="open circuit"),
        pytest.param(3.3, id="shorted to vcc"),
        pytest.param(3.4, id="noise above vcc"),
    ],
)
def test_calc_temp_rejects_a_thermistor_at_the_rails(v_adc: float) -> None:
    with pytest.raises(ThermalSensorError):
        SolarSimulator._calc_temp(v_adc)


def test_calc_temp_reads_a_healthy_thermistor() -> None:
    assert SolarSimulator._calc_temp(1.65) == pytest.approx(25.0, abs=0.01)


def test_blank_darkens_the_lights_without_forgetting_the_setting() -> None:
    sim = SolarSimulator()
    sim.set_leds(v=1000, w=2000, c=3000, h=4000)

    sim.blank()

    assert sim.mcp.channel_a.value == 0
    assert sim.hal.duty_cycle == 0
    assert sim.current_light_settings == {'v': 1000, 'w': 2000, 'c': 3000, 'h': 4000}


def test_restore_drives_the_recorded_setting_again() -> None:
    sim = SolarSimulator()
    sim.set_leds(v=1000, w=2000, c=3000, h=4000)
    sim.blank()

    sim.restore()

    assert sim.mcp.channel_a.value == 1000
    assert sim.hal.duty_cycle == 4000
