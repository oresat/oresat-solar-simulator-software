from solar_simulator import SolarSimulator
from solar_simulator.lib.stubs import StubADS1015, StubI2C, StubMCP4728, StubPWMOut


def make_sim() -> SolarSimulator:
    return SolarSimulator(StubADS1015(), StubPWMOut(), StubI2C(), StubMCP4728())


def test_set_leds_updates_state() -> None:
    # Arrange
    sim = make_sim()
    # Act
    sim.set_leds(v=1000, w=2000, c=3000, h=4000)
    # Assert
    assert sim.current_light_settings == {'v': 1000, 'w': 2000, 'c': 3000, 'h': 4000}
    assert sim.mcp.channel_a.value == 1000
    assert sim.mcp.channel_b.value == 2000
    assert sim.mcp.channel_c.value == 3000
    assert sim.hal.duty_cycle == 4000
