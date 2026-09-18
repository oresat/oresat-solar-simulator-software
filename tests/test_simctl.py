import pytest
from simctl import SWEEP_STEPS, sweep


def test_sweep_starts_and_ends_dark() -> None:
    points = sweep(1.0)

    assert len(points) == SWEEP_STEPS
    assert points[0] == 0
    assert points[-1] == 0


@pytest.mark.parametrize("peak", [0.0, 0.25, 0.5, 1.0])
def test_sweep_reaches_the_peak_halfway_through(peak: float) -> None:
    points = sweep(peak)

    assert max(points) == round(peak * 100)
    assert points[SWEEP_STEPS // 2] == round(peak * 100)


def test_sweep_never_leaves_the_range_the_protocol_accepts() -> None:
    assert all(0 <= point <= 100 for point in sweep(1.0))
