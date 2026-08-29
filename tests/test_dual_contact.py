from src.dual_contact import run


def test_dual_contact_regulates_both_surfaces() -> None:
    metrics = run(steps=1200)
    assert metrics.contacts_seen
    assert abs(metrics.mean_floor_force_n - 5.0) < 0.3
    assert abs(metrics.mean_wall_force_n - 4.0) < 0.3
    assert metrics.max_floor_penetration_m < 0.001
    assert metrics.max_wall_penetration_m < 0.001
    assert metrics.control_limit_violations == 0
    assert metrics.force_limit_violations == 0


def test_dual_contact_is_deterministic() -> None:
    assert run(steps=400, seed=101) == run(steps=400, seed=101)


def test_dual_contact_rejects_invalid_targets() -> None:
    try:
        run(steps=100, target_wall_force_n=0.0)
    except ValueError as exc:
        assert "target forces" in str(exc)
    else:
        raise AssertionError("invalid target force was accepted")
