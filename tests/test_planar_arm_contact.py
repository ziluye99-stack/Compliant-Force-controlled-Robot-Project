from src.planar_arm_contact import run


def test_planar_arm_reaches_contact_and_tracks_normal_force() -> None:
    metrics = run(steps=1500, target_normal_force_n=5.0, target_tangential_force_n=0.0)
    assert metrics.contacts_seen
    assert abs(metrics.mean_normal_force_n - 5.0) < 0.2
    assert metrics.max_joint_torque_nm <= 20.0
    assert metrics.max_penetration_m < 0.002


def test_planar_arm_tangential_force_respects_friction_limit() -> None:
    metrics = run(steps=1500, target_normal_force_n=5.0, target_tangential_force_n=1.0, friction_coefficient=0.5)
    assert metrics.contacts_seen
    assert metrics.mean_tangential_force_n <= 0.5 * metrics.mean_normal_force_n + 0.3
    assert metrics.max_position_error_m < 0.1


def test_planar_arm_is_deterministic() -> None:
    assert run(steps=500, target_tangential_force_n=0.0) == run(steps=500, target_tangential_force_n=0.0)
