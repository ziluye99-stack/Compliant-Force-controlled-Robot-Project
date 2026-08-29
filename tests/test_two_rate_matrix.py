import json

from src.analyze_two_rate_matrix import bootstrap_mean_ci, summarize_rows
from src.two_rate_matrix import matrix_cases, run_matrix


def _config() -> dict:
    return {
        "experiment": {"name": "test", "artifact_root": "artifacts/test"},
        "interface_contract": "configs/platform_neutral_interface.yaml",
        "control": {"residual_period_fast_steps": 5},
        "variants": ["pi_only", "joint_residual"],
        "training": {
            "target_force_range_n": [3.0, 7.0],
            "episodes": 2,
            "steps_per_episode": 20,
            "seeds": [101, 202],
            "dynamics": {"nominal": {"damping_scale": 1.5, "actuator_gain": 0.8}},
        },
        "evaluation": {
            "target_force_n": [4.0, 6.0],
            "heldout_dynamics": {
                "friction_scale": [0.75, 1.25],
                "stiffness_scale": [0.8, 1.2],
                "force_noise_std_n": [0.1],
                "actuator_delay_steps": [0, 2],
            },
            "steps": 40,
        },
    }


def test_matrix_expands_cartesian_product() -> None:
    cases = matrix_cases(_config())
    assert len(cases) == 2 * 2 * 2 * 2 * 2 * 1 * 2
    assert cases[0]["variant"] == "pi_only"
    assert cases[-1]["actuator_delay_steps"] == 2


def test_matrix_dry_run_is_side_effect_free(tmp_path) -> None:
    artifact_dir = tmp_path / "run"
    output = run_matrix(_config(), artifact_dir, max_cases=1, dry_run=True)
    assert output["manifest"]["requested_case_count"] == 64
    assert output["manifest"]["executed_case_count"] == 1
    assert output["manifest"]["interface_contract"]["name"] == "platform-neutral-contact-force-v1"
    assert output["manifest"]["interface_contract"]["safety"]["hardware_commands_enabled"] is False
    assert len(output["cases"]) == 1
    assert not artifact_dir.exists()


def test_matrix_smoke_writes_provenance_and_results(tmp_path) -> None:
    artifact_dir = tmp_path / "run"
    config = _config()
    config["variants"] = ["joint_residual"]
    output = run_matrix(
        config, artifact_dir, max_cases=1, episodes=2, steps=20, eval_steps=40,
    )
    assert output["manifest"]["executed_case_count"] == 1
    assert (artifact_dir / "manifest.json").is_file()
    assert (artifact_dir / "config.yaml").is_file()
    results = json.loads((artifact_dir / "results.json").read_text())
    assert len(results) == 1
    assert results[0]["case"]["variant"] == "joint_residual"
    assert results[0]["result"]["residual"]["contacts_seen"]
    assert results[0]["result"]["baseline"]["contacts_seen"]
    artifact_dir = artifact_dir / "cases" / "0000-joint_residual"
    assert (artifact_dir / "dataset.npz").is_file()
    assert (artifact_dir / "train.npz").is_file()
    assert (artifact_dir / "test.npz").is_file()
    assert (artifact_dir / "policy.npz").is_file()
    assert results[0]["training_artifact_dir"] == "cases/0000-joint_residual"
    assert results[0]["result"]["training_artifacts"]["policy"] == "policy.npz"


def test_summary_reports_paired_delta_and_deterministic_ci() -> None:
    metrics = {
        "force_rmse_n": 1.0,
        "measured_force_rmse_n": 1.0,
        "tail_abs_error_n": 1.0,
        "max_penetration_m": 0.001,
        "peak_force_n": 2.0,
        "contact_loss_rate": 0.0,
        "max_abs_control_n": 3.0,
        "safety_gate_activations": 0,
    }
    rows = [
        {"case": {"variant": "pi_only", "target_force_n": 4.0, "seed": 1}, "result": {"baseline": metrics}},
        {"case": {"variant": "joint_residual", "target_force_n": 4.0, "seed": 1}, "result": {"baseline": metrics, "residual": {**metrics, "force_rmse_n": 0.8}}},
    ]
    summary = summarize_rows(rows, replicates=50, seed=9)
    assert summary["case_count"] == 2
    assert summary["variants"]["joint_residual"]["force_rmse_n"]["mean"] == 0.8
    assert abs(summary["paired_delta_residual_minus_pi"]["joint_residual"]["force_rmse_n"]["mean_delta"] + 0.2) < 1e-12
    assert bootstrap_mean_ci([1.0], replicates=10) == (1.0, 1.0)
