from pathlib import Path

from src.contact_data import read_contact_log
from src.mujoco_contact_trace import export_trace, run_trace


def test_mujoco_trace_has_no_contact_and_contact_phases() -> None:
    samples = run_trace(steps=500, pre_contact_steps=50, target_tangential_force_n=1.0)
    assert len(samples) == 500
    assert not any(sample.contact for sample in samples[:50])
    assert any(sample.contact for sample in samples[50:])
    assert samples[0].timestamp_s == 0.0
    assert samples[-1].timestamp_s > samples[0].timestamp_s


def test_mujoco_trace_exports_schema_and_reports_replay(tmp_path: Path) -> None:
    output = tmp_path / "mujoco.csv"
    report = export_trace(output, steps=500, pre_contact_steps=50)
    samples, metadata = read_contact_log(output)
    assert report["sample_count"] == 500
    assert len(samples) == 500
    assert metadata["source"] == "mujoco"
    assert report["replay"]["safe_to_replay"]
