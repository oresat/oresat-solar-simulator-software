import pytest

from solar_simulator import SolarSimulator
from solar_simulator.lib import thermal
from solar_simulator.lib.solar_simulator import ThermalSensorError


def test_enforce_thermal_limits_darkens_the_lights_and_puts_them_back(
    sim: SolarSimulator,
) -> None:
    sim.set_intensity(1.0)
    commanded = dict(sim.current_light_settings)
    sim.check_thermals.side_effect = [
        [120.0, 25.0, 25.0],  # past the LED's shutdown limit
        [40.0, 25.0, 25.0],  # under the resume limit, so the latch clears
    ]

    assert thermal.enforce_thermal_limits(sim, writer=lambda _message: None) is True

    assert sim.current_light_settings == commanded
    assert sim.mcp.channel_a.value == commanded['v']
    assert sim.hal.duty_cycle == commanded['h']


def test_enforce_thermal_limits_raises_when_the_sensors_cannot_be_read(sim: SolarSimulator) -> None:
    sim.check_thermals.side_effect = ThermalSensorError("Thermistor voltage out of range: 0.000V")

    with pytest.raises(ThermalSensorError):
        thermal.enforce_thermal_limits(sim, writer=lambda _message: None)
