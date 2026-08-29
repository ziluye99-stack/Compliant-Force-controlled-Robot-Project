from src.contact_force_baseline import run


def test_normal_force_baseline_reaches_contact_and_tracks_target() -> None:
    metrics = run(steps=2000, target_force_n=5.0)
    assert metrics.contacts_seen
    assert abs(metrics.mean_force_n - metrics.target_force_n) < 0.02
    assert metrics.force_rmse_n < 0.05
    assert metrics.max_penetration_m < 0.001


def test_normal_force_baseline_is_deterministic() -> None:
    assert run(steps=500) == run(steps=500)
