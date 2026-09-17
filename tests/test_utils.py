from unittest.mock import MagicMock

from solar_simulator.lib import utils


def test_check_temperature_waits_for_every_sensor_to_cool(sim: MagicMock) -> None:
    # The LED runs hot on its own; the heatsink and cell are under the resume limit
    # from the first reading, so a check that needs all three to be hot never waits.
    sim.check_thermals.side_effect = [
        [120.0, 25.0, 25.0],
        [90.0, 25.0, 25.0],
        [40.0, 25.0, 25.0],
    ]

    utils.check_temperature(sim, writer=lambda _message: None)

    assert sim.check_thermals.call_count == 3
