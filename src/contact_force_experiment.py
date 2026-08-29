"""Run the deterministic MuJoCo force baseline from a YAML configuration."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from .contact_force_baseline import run
from .experiment import REPOSITORY_ROOT, interface_contract_summary, load_config, package_snapshot


def _git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _section(config: dict[str, Any], name: str) -> dict[str, Any]:
    value = config.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def run_from_config(
    config: dict[str, Any],
    artifact_dir: Path,
    *,
    seed: int | None = None,
    steps: int | None = None,
) -> dict[str, Any]:
    """Resolve one YAML config, execute the baseline, and write provenance."""
    task = _section(config, "task")
    controller = _section(config, "controller")
    disturbance = _section(config, "disturbance")
    experiment = _section(config, "experiment")
    actual_seed = int(seed if seed is not None else experiment.get("seed", task.get("seed", 42)))
    actual_steps = int(steps if steps is not None else task.get("steps", 2000))
    metrics = run(
        steps=actual_steps,
        target_force_n=float(task.get("target_force_n", 5.0)),
        kp=float(controller.get("kp", 0.5)),
        ki=float(controller.get("ki", 5.0)),
        kd=float(controller.get("kd", 0.3)),
        integral_limit=float(controller.get("integral_limit", 10.0)),
        control_limit_n=float(controller.get("control_limit_n", 30.0)),
        force_noise_std_n=float(disturbance.get("force_noise_std_n", 0.0)),
        damping_scale=float(disturbance.get("damping_scale", 1.0)),
        actuator_gain=float(disturbance.get("actuator_gain", 1.0)),
        friction_scale=float(disturbance.get("friction_scale", 1.0)),
        actuator_delay_steps=int(disturbance.get("actuator_delay_steps", 0)),
        seed=actual_seed,
    )
    artifact_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": artifact_dir.name,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config_name": experiment.get("name"),
        "config_path": "configs/contact_force.yaml",
        "git_commit": _git_revision(),
        "python": sys.version,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "artifact_dir": str(artifact_dir),
        "seed": actual_seed,
        "steps": actual_steps,
        "package_snapshot": package_snapshot(),
        "interface_contract": interface_contract_summary(config),
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifact_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    metric_data = asdict(metrics)
    (artifact_dir / "metrics.json").write_text(json.dumps(metric_data, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "metrics": metric_data}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/contact_force.yaml"))
    parser.add_argument("--run-id")
    parser.add_argument("--steps", type=int)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    config = load_config(args.config)
    experiment = _section(config, "experiment")
    run_id = args.run_id or experiment.get("run_id") or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_root = REPOSITORY_ROOT / str(experiment.get("artifact_root", "artifacts/contact-force-baseline"))
    result = run_from_config(config, artifact_root / str(run_id), seed=args.seed, steps=args.steps)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
