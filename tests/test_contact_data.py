from pathlib import Path

from src.contact_data import (
    identify_parameters,
    read_contact_log,
    replay_safety_check,
    synthetic_calibration_log,
    write_contact_log,
)


def test_contact_log_round_trip_and_metadata(tmp_path: Path) -> None:
    samples = synthetic_calibration_log(samples_per_phase=8)
    path = tmp_path / "contact.csv"
    write_contact_log(path, samples, {"git_commit": "test"})
    loaded, metadata = read_contact_log(path)
    assert loaded == samples
    assert metadata["schema_version"] == "contact-log/v1"
    assert metadata["git_commit"] == "test"


def test_identification_recovers_synthetic_bias_noise_and_friction() -> None:
    result = identify_parameters(synthetic_calibration_log(samples_per_phase=100, seed=7))
    assert result.valid
    assert abs(result.normal_bias_n - 0.12) < 0.01
    assert result.normal_noise_std_n < 0.04
    assert result.friction_coefficient is not None
    assert abs(result.friction_coefficient - 0.45) < 0.02


def test_replay_check_rejects_command_limit_violation() -> None:
    samples = synthetic_calibration_log(samples_per_phase=8)
    report = replay_safety_check(samples, tangential_command_limit_n=3.0)
    assert not report.within_limits
    assert not report.safe_to_replay
