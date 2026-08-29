import json

from src.variable_compliance_matrix import matrix_cases, run_matrix


def _config() -> dict:
    return {
        "experiment": {"name": "test-variable", "artifact_root": "artifacts/test-variable"},
        "task": {"initial_offset_m": 0.012, "target_depth_qpos_m": -0.08, "search_depth_qpos_m": -0.035, "steps": 500, "seeds": [1]},
        "control": {"outer_period_fast_steps": 25, "force_limit_n": 80.0, "intrusion_limit_m": 0.006, "strategies": ["fixed"]},
        "contact": {"friction_coefficient": 0.7},
        "matrix": {"strategies": ["fixed", "variable"], "seeds": [1, 2], "initial_offsets_m": [0.01, 0.012], "friction_coefficients": [0.6, 0.7]},
    }


def test_matrix_expands_all_axes() -> None:
    cases = matrix_cases(_config())
    assert len(cases) == 16
    assert cases[0] == {"strategy": "fixed", "seed": 1, "initial_offset_m": 0.01, "friction_coefficient": 0.6}
    assert cases[-1]["strategy"] == "variable"


def test_dry_run_has_no_side_effect(tmp_path) -> None:
    artifact_dir = tmp_path / "run"
    output = run_matrix(_config(), artifact_dir, max_cases=1, dry_run=True)
    assert output["manifest"]["requested_case_count"] == 16
    assert output["manifest"]["executed_case_count"] == 1
    assert not artifact_dir.exists()


def test_matrix_writes_manifest_and_retains_rows(tmp_path) -> None:
    artifact_dir = tmp_path / "run"
    output = run_matrix(_config(), artifact_dir, max_cases=1)
    assert output["manifest"]["failure_count"] == 0
    assert (artifact_dir / "manifest.json").is_file()
    rows = json.loads((artifact_dir / "results.json").read_text())
    assert rows[0]["status"] == "completed"
    assert rows[0]["metrics"]["seed"] == 1
