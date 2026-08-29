import json
from pathlib import Path

from src.contact_force_experiment import run_from_config
from src.experiment import load_config


def test_config_driven_baseline_writes_provenance_and_metrics(tmp_path: Path) -> None:
    config = load_config(Path("configs/contact_force.yaml"))
    result = run_from_config(config, tmp_path / "run", seed=17, steps=200)
    run_dir = tmp_path / "run"
    assert result["manifest"]["seed"] == 17
    assert result["manifest"]["steps"] == 200
    assert result["manifest"]["interface_contract"]["simulator"] == "mujoco"
    assert (run_dir / "config.yaml").is_file()
    assert (run_dir / "manifest.json").is_file()
    assert (run_dir / "metrics.json").is_file()
    assert json.loads((run_dir / "metrics.json").read_text())["contacts_seen"] is True
