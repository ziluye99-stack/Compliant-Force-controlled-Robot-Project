from src.contact_force_baseline import run


def test_normal_force_baseline_reaches_contact_and_tracks_target() -> None:
    metrics = run(steps=2000, target_force_n=5.0)
    assert metrics.contacts_seen
    assert abs(metrics.mean_force_n - metrics.target_force_n) < 0.02
    assert metrics.force_rmse_n < 0.05
    assert metrics.max_penetration_m < 0.001


def test_normal_force_baseline_is_deterministic() -> None:
    assert run(steps=500) == run(steps=500)


def test_baseline_handles_sensor_noise_and_dynamics_mismatch() -> None:
    metrics = run(
        steps=3000,
        target_force_n=5.0,
        force_noise_std_n=0.2,
        damping_scale=1.5,
        actuator_gain=0.8,
        actuator_delay_steps=10,
        seed=7,
    )
    assert metrics.contacts_seen
    assert abs(metrics.mean_force_n - metrics.target_force_n) < 0.1
    assert metrics.force_rmse_n < 0.15
