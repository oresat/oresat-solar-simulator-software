from solar_simulator import SolarSimulator


def test_set_leds_updates_state() -> None:
    # Arrange
    sim = SolarSimulator()
    # Act
    sim.set_leds(v=1000, w=2000, c=3000, h=4000)
    # Assert
    assert sim.current_light_settings == {'v': 1000, 'w': 2000, 'c': 3000, 'h': 4000}
    assert sim.mcp.channel_a.value == 1000
    assert sim.mcp.channel_b.value == 2000
    assert sim.mcp.channel_c.value == 3000
    assert sim.hal.duty_cycle == 4000
