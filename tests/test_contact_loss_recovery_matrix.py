from pathlib import Path

from src.contact_loss_recovery_matrix import run_matrix, run_matrix_from_config


ROOT = Path(__file__).resolve().parents[1]


def test_matrix_retains_nominal_success_and_large_disturbance_failure() -> None:
    result = run_matrix(
        steps=500,
        disturbance_step=200,
        separation_impulses=(0.2, 1.0),
        force_noise_stds=(0.0,),
        damping_scales=(1.0,),
        actuator_delays=(0,),
    )

    assert result["schema_version"] == "contact-loss-recovery-matrix/v1"
    assert result["case_count"] == 2
    assert result["safe_recovery_count"] == 1
    assert result["failure_count"] == 1
    cases = result["cases"]
    assert isinstance(cases, list)
    assert cases[0]["safe_recovery"] is True
    assert cases[1]["safe_recovery"] is False
    assert cases[1]["force_limit_violations"] > 0


def test_matrix_is_deterministic_with_a_fixed_seed() -> None:
    kwargs = dict(
        steps=500,
        disturbance_step=200,
        separation_impulses=(0.2,),
        force_noise_stds=(0.1,),
        damping_scales=(0.5, 1.0),
        actuator_delays=(0, 2),
        seed=7,
    )
    assert run_matrix(**kwargs) == run_matrix(**kwargs)


def test_matrix_rejects_empty_axis() -> None:
    try:
        run_matrix(separation_impulses=())
    except ValueError as exc:
        assert "axis" in str(exc)
    else:
        raise AssertionError("empty matrix axis was accepted")


def test_committed_yaml_drives_the_matrix() -> None:
    result = run_matrix_from_config(ROOT / "configs/contact_loss_recovery_matrix.yaml")
    assert result["config_path"].endswith("configs/contact_loss_recovery_matrix.yaml")
    assert result["case_count"] == 36
    assert result["axes"]["actuator_delay_steps"] == [0, 2]
