"""Tests to exercise the SolarSimulator lib module code."""


def test_initial_duty_cycle_is_zero(solar_simulator):
    """SolarSimulator initializes with lights off."""
    sim, fake_pwm = solar_simulator

    assert sim.light_settings ["h"] == 0
