import pytest

from solar_simulator import SolarSimulator
from solar_simulator.lib import thermal
from solar_simulator.lib.solar_simulator import ThermalSensorError


def test_enforce_thermal_limits_waits_for_every_sensor_to_cool(sim: SolarSimulator) -> None:
    # The LED runs hot on its own; the heatsink and cell are under the resume limit
    # from the first reading, so a check that needs all three to be hot never waits.
    sim.check_thermals.side_effect = [
        [120.0, 25.0, 25.0],
        [90.0, 25.0, 25.0],
        [40.0, 25.0, 25.0],
    ]

    thermal.enforce_thermal_limits(sim, writer=lambda _message: None)

    assert sim.check_thermals.call_count == 3


def test_enforce_thermal_limits_raises_when_the_sensors_cannot_be_read(sim: SolarSimulator) -> None:
    sim.check_thermals.side_effect = ThermalSensorError("Thermistor voltage out of range: 0.000V")

    with pytest.raises(ThermalSensorError):
        thermal.enforce_thermal_limits(sim, writer=lambda _message: None)
