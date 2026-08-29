import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.experiment import interface_contract_summary
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
    assert manifest["interface_contract"]["name"] == "platform-neutral-contact-force-v1"
    assert manifest["interface_contract"]["version"] == 1
    assert manifest["interface_contract"]["timing"]["fast_controller_hz"] == 500
    assert manifest["interface_contract"]["timing"]["policy_hz"] == 20
    assert manifest["interface_contract"]["safety"]["hardware_commands_enabled"] is False


def test_mujoco_smoke_is_deterministic() -> None:
    assert run(100) == run(100)
    assert run(100) > 0


def test_missing_interface_contract_is_rejected() -> None:
    with pytest.raises(ValueError, match="interface_contract"):
        interface_contract_summary({})
