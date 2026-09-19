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


def test_stub_i2c_reports_the_devices_it_stands_in_for() -> None:
    # Arrange
    i2c = StubI2C()
    # Act / Assert
    assert i2c.try_lock() is True
    assert i2c.scan() == [0x48, 0x60]
    assert i2c.unlock() is None
