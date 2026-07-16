"""Tests to exercise the SolarSimulator lib module code."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from solar_simulator import SolarSimulator


def test_initial_duty_cycle_is_zero(solar_simulator: tuple[SolarSimulator, MagicMock]) -> None:
    """Ensure SolarSimulator initializes with lights off."""
    sim, _fake_pwm = solar_simulator

    assert sim.light_settings["h"] == 0


def test_set_lights_updates_halogen(solar_simulator: tuple[SolarSimulator, MagicMock]) -> None:
    """Ensure SolarSimulator.set_lights sets the halogen light intensity."""
    sim, _fake_pwm = solar_simulator
    sim.set_lights(100)

    assert sim.light_settings["h"] == 100
