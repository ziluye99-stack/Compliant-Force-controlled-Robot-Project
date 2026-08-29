"""Create a reproducible run manifest without assuming a robot implementation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from .interface_contract import load_summary


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    defaults = config.pop("defaults", [])
    merged: dict[str, Any] = {}
    for default in defaults:
        if not isinstance(default, str):
            raise ValueError(f"Config defaults must be filenames: {path}")
        base_path = path.parent / f"{default}.yaml"
        merged.update(load_config(base_path))
    for key, value in config.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


def git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def package_snapshot() -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines() if result.returncode == 0 else []


def interface_contract_summary(config: dict[str, Any]) -> dict[str, Any]:
    reference = config.get("interface_contract")
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("interface_contract must reference a YAML contract")
    path = Path(reference).expanduser()
    if not path.is_absolute():
        path = REPOSITORY_ROOT / path
    return load_summary(path.resolve())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    interface = interface_contract_summary(config)
    experiment = config.setdefault("experiment", {})
    run_id = experiment.get("run_id") or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_root = REPOSITORY_ROOT / experiment.get("artifact_root", "artifacts")
    artifact_dir = artifact_root / str(run_id)

    manifest = {
        "run_id": run_id,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config_path": str(args.config),
        "git_commit": git_revision(),
        "python": sys.version,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "artifact_dir": str(artifact_dir),
        "package_snapshot": package_snapshot(),
        "interface_contract": interface,
    }

    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return

    artifact_dir.mkdir(parents=True, exist_ok=False)
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifact_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    print(f"Created run manifest: {artifact_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
