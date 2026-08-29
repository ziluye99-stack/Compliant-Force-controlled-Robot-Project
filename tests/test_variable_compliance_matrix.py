import json

import src.variable_compliance_matrix as matrix_module
from src.variable_compliance_matrix import matrix_cases, run_matrix
from src.variable_compliance_peg import PegInHoleMetrics


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
    assert rows[0]["outcome"] == "success"
    assert rows[0]["metrics"]["seed"] == 1


def test_unsuccessful_outcomes_count_as_failures(tmp_path, monkeypatch) -> None:
    unsuccessful = PegInHoleMetrics(
        strategy="fixed", seed=1, success=False, steps=500,
        peak_contact_force_n=1.0, contact_active_mean_force_n=1.0,
        tail_mean_contact_force_n=1.0, max_lateral_contact_force_n=1.0,
        final_lateral_error_m=0.02, max_geometric_intrusion_m=0.01,
        safety_gate_activations=3, contacts_seen=True, outer_updates=20,
    )
    monkeypatch.setattr(matrix_module, "run", lambda **kwargs: unsuccessful)
    output = run_matrix(_config(), tmp_path / "run", max_cases=1)
    assert output["manifest"]["failure_count"] == 1
    assert output["manifest"]["unsuccessful_case_count"] == 1
    assert output["manifest"]["execution_error_count"] == 0
    row = output["results"][0]
    assert row["status"] == "completed"
    assert row["outcome"] == "unsuccessful"
