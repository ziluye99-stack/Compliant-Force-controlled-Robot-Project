from src.variable_compliance_peg import run


def test_variable_compliance_is_deterministic() -> None:
    assert run("variable", steps=500, seed=42) == run("variable", steps=500, seed=42)


def test_both_strategies_insert_within_safety_envelope() -> None:
    for strategy in ("fixed", "variable"):
        metrics = run(strategy, steps=1500, seed=42)
        assert metrics.contacts_seen
        assert metrics.success
        assert metrics.max_geometric_intrusion_m <= 0.006
        assert metrics.peak_contact_force_n <= 80.0


def test_variable_schedule_reduces_peak_contact_force_in_nominal_scene() -> None:
    fixed = run("fixed", steps=1500, seed=42)
    variable = run("variable", steps=1500, seed=42)
    assert fixed.success and variable.success
    assert variable.peak_contact_force_n < fixed.peak_contact_force_n


def test_variable_schedule_has_expected_outer_rate() -> None:
    metrics = run("variable", steps=1500, seed=42, outer_period_fast_steps=25)
    assert metrics.outer_updates == 60
