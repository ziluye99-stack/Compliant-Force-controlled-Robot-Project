from src.contact_loss_recovery import run


def test_contact_loss_is_detected_and_recovered() -> None:
    metrics = run(steps=900, disturbance_step=300, separation_impulse_m_s=0.2)
    assert metrics.contact_loss_detected
    assert metrics.recovery_detected
    assert metrics.loss_duration_steps is not None
    assert metrics.recovery_time_s is not None
    assert metrics.recovery_time_s < 0.5
    assert metrics.peak_force_after_disturbance_n < 40.0
    assert metrics.control_limit_violations == 0
    assert metrics.force_limit_violations == 0
    assert metrics.safety_gate_activations == 0


def test_large_disturbance_reports_baseline_safety_failure() -> None:
    metrics = run(steps=1200, disturbance_step=400, separation_impulse_m_s=1.0)
    assert metrics.contact_loss_detected
    assert metrics.recovery_detected
    assert metrics.force_limit_violations > 0
    assert metrics.safety_gate_activations > 0


def test_contact_loss_recovery_is_deterministic() -> None:
    assert run(steps=700, disturbance_step=200) == run(steps=700, disturbance_step=200)


def test_no_disturbance_is_not_reported_as_recovery() -> None:
    metrics = run(steps=700, disturbance_step=200, separation_impulse_m_s=0.0)
    assert not metrics.contact_loss_detected
    assert not metrics.recovery_detected
    assert metrics.recovery_time_s is None


def test_contact_loss_recovery_rejects_invalid_window() -> None:
    try:
        run(steps=100, disturbance_step=90)
    except ValueError as exc:
        assert "leave room" in str(exc)
    else:
        raise AssertionError("invalid disturbance window was accepted")
