import json
import subprocess
import sys
from pathlib import Path

from src.mujoco_smoke import run


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_records_reproducibility_metadata() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.experiment", "--config", "configs/sim.yaml", "--dry-run"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = json.loads(result.stdout)
    assert manifest["run_id"]
    assert manifest["git_commit"]
    assert manifest["slurm_job_id"] is None
    assert manifest["artifact_dir"].endswith(manifest["run_id"])


def test_mujoco_smoke_is_deterministic() -> None:
    assert run(100) == run(100)
    assert run(100) > 0
