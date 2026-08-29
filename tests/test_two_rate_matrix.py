import json

from src.two_rate_matrix import matrix_cases, run_matrix


def _config() -> dict:
    return {
        "experiment": {"name": "test", "artifact_root": "artifacts/test"},
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
