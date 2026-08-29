from src.tangential_contact import run


def test_low_tangential_force_stays_below_friction_limit() -> None:
    metrics = run(steps=1200, target_normal_force_n=5.0, target_tangential_force_n=1.0, friction_coefficient=0.5)
    assert metrics.contacts_seen
    assert abs(metrics.mean_normal_force_n - 5.0) < 0.1
    assert metrics.mean_tangential_force_n > 0.5
    assert metrics.friction_ratio < 0.5
    assert not metrics.slipped
    assert metrics.max_penetration_m < 0.001


def test_high_tangential_force_reaches_sliding_regime() -> None:
    metrics = run(steps=1200, target_normal_force_n=5.0, target_tangential_force_n=4.0, friction_coefficient=0.5)
    assert metrics.contacts_seen
    assert metrics.mean_tangential_force_n <= metrics.friction_coefficient * metrics.mean_normal_force_n + 0.2
    assert metrics.slipped
    assert metrics.max_penetration_m < 0.001


def test_contact_task_is_deterministic() -> None:
    assert run(steps=500, target_tangential_force_n=1.0) == run(steps=500, target_tangential_force_n=1.0)
