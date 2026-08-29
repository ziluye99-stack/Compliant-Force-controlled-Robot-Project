"""Run the YAML-defined variable-compliance peg-in-hole matrix.

This is a simulation-only batch entry point. It records provenance and writes
results after every case so interrupted runs retain successful and failed
cases for inspection. It never submits jobs or sends hardware commands.
"""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from .experiment import load_config, package_snapshot
from .variable_compliance_peg import run


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _axis(value: Any, name: str) -> list[Any]:
    if isinstance(value, list):
        if not value:
            raise ValueError(f"{name} must be non-empty")
        return value
    if value is None:
        raise ValueError(f"{name} must be provided")
    return [value]


def matrix_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand strategy, seed, offset, and friction axes deterministically."""
    task = config.get("task", {})
    control = config.get("control", {})
    contact = config.get("contact", {})
    matrix = config.get("matrix", {})
    if not all(isinstance(section, dict) for section in (task, control, contact, matrix)):
        raise ValueError("task, control, contact, and matrix must be mappings")
    strategies = _axis(matrix.get("strategies", control.get("strategies")), "strategies")
    seeds = _axis(matrix.get("seeds", task.get("seeds")), "seeds")
    offsets = _axis(matrix.get("initial_offsets_m", task.get("initial_offset_m")), "initial_offsets_m")
    frictions = _axis(matrix.get("friction_coefficients", contact.get("friction_coefficient")), "friction_coefficients")
    unknown = set(strategies) - {"fixed", "variable"}
    if unknown:
        raise ValueError(f"unknown strategies: {sorted(unknown)}")
    cases: list[dict[str, Any]] = []
    for strategy, seed, offset, friction in itertools.product(strategies, seeds, offsets, frictions):
        offset_value = float(offset)
        friction_value = float(friction)
        if int(seed) < 0:
            raise ValueError("seeds must be non-negative")
        if offset_value < 0:
            raise ValueError("initial_offsets_m must be non-negative")
        if friction_value <= 0:
            raise ValueError("friction_coefficients must be positive")
        cases.append({
            "strategy": str(strategy),
            "seed": int(seed),
            "initial_offset_m": offset_value,
            "friction_coefficient": friction_value,
        })
    return cases


def _git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, check=False,
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def run_matrix(
    config: dict[str, Any], artifact_dir: Path, *, max_cases: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    cases = matrix_cases(config)
    if max_cases is not None:
        if max_cases < 1:
            raise ValueError("max_cases must be positive")
        cases = cases[:max_cases]
    task = config["task"]
    control = config["control"]
    contact = config["contact"]
    manifest: dict[str, Any] = {
        "run_id": artifact_dir.name,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config_name": config.get("experiment", {}).get("name"),
        "git_commit": _git_revision(),
        "python": sys.version,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "artifact_dir": str(artifact_dir),
        "requested_case_count": len(matrix_cases(config)),
        "executed_case_count": len(cases),
        "failure_count": 0,
        "package_snapshot": package_snapshot(),
        "simulation": {
            "steps": int(task.get("steps", 1500)),
            "outer_period_fast_steps": int(control.get("outer_period_fast_steps", 25)),
            "target_depth_qpos_m": float(task.get("target_depth_qpos_m", -0.080)),
            "search_depth_qpos_m": float(task.get("search_depth_qpos_m", -0.035)),
            "force_limit_n": float(control.get("force_limit_n", 80.0)),
            "intrusion_limit_m": float(control.get("intrusion_limit_m", 0.006)),
        },
    }
    if dry_run:
        return {"manifest": manifest, "cases": cases}

    artifact_dir.mkdir(parents=True, exist_ok=False)
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifact_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    results: list[dict[str, Any]] = []
    results_path = artifact_dir / "results.json"
    for index, case in enumerate(cases):
        try:
            metrics = run(
                strategy=case["strategy"],
                steps=manifest["simulation"]["steps"],
                seed=case["seed"],
                initial_offset_m=case["initial_offset_m"],
                friction_coefficient=case["friction_coefficient"],
                outer_period_fast_steps=manifest["simulation"]["outer_period_fast_steps"],
                target_depth_qpos_m=manifest["simulation"]["target_depth_qpos_m"],
                search_depth_qpos_m=manifest["simulation"]["search_depth_qpos_m"],
                force_limit_n=manifest["simulation"]["force_limit_n"],
                intrusion_limit_m=manifest["simulation"]["intrusion_limit_m"],
            )
            row = {"index": index, "case": case, "status": "completed", "metrics": metrics.__dict__}
        except Exception as exc:  # retain failures as first-class matrix evidence
            manifest["failure_count"] += 1
            row = {"index": index, "case": case, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
        results.append(row)
        results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/variable_compliance_peg.yaml"))
    parser.add_argument("--run-id")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    experiment = config.get("experiment", {})
    run_id = args.run_id or experiment.get("run_id") or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_dir = REPOSITORY_ROOT / str(experiment.get("artifact_root", "artifacts/variable-compliance-peg")) / str(run_id)
    output = run_matrix(config, artifact_dir, max_cases=args.max_cases, dry_run=args.dry_run)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
