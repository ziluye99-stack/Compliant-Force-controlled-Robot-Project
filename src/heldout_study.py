"""Held-out target-force and dynamics study for the residual baseline."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .contact_force_baseline import run
from .experiment import REPOSITORY_ROOT, git_revision, load_config, package_snapshot
from .residual_policy import ResidualLinearPolicy, _config_values, collect_dataset, evaluate_residual, split_by_episode


def run_study(
    *,
    train_episodes: int = 12,
    train_steps: int = 500,
    eval_steps: int = 1000,
    seed: int = 42,
    config: dict[str, Any] | None = None,
    train_fraction: float = 0.8,
) -> list[dict[str, object]]:
    """Train on a target range and evaluate held-out target/dynamics settings."""
    force_noise_std_n = 0.2
    damping_nominal, actuator_nominal, friction_nominal, delay_steps = 1.5, 0.8, 1.0, 0
    controller = {"kp": 0.5, "ki": 5.0, "kd": 0.3, "integral_limit": 10.0, "control_limit_n": 30.0}
    target_range = (3.0, 7.0)
    heldout_targets, heldout_damping, heldout_gain, eval_seeds = (4.0, 6.0), (1.2, 1.8), (0.9, 0.7), (101, 202, 303)
    ridge, residual_limit = 1e-3, 10.0
    randomization = ((1.2, 1.8), (0.7, 0.9))
    if config is not None:
        values = _config_values(config)
        learning = config.get("learning", {})
        heldout = config.get("heldout", {})
        controller = {name: values[name] for name in ("kp", "ki", "kd", "integral_limit", "control_limit_n")}
        force_noise_std_n = values["force_noise_std_n"]
        damping_nominal, actuator_nominal, friction_nominal, delay_steps = (values[name] for name in ("damping_scale", "actuator_gain", "friction_scale", "actuator_delay_steps"))
        target_range = values["target_range"]
        train_fraction = float(values["train_fraction"])
        ridge, residual_limit = values["ridge"], values["residual_limit_n"]
        randomization = values["dynamics_randomization"]
        if not isinstance(learning, dict) or not isinstance(heldout, dict):
            raise ValueError("learning and heldout must be mappings")
        heldout_targets = tuple(float(v) for v in heldout.get("target_force_n", heldout_targets))
        heldout_damping = tuple(float(v) for v in heldout.get("damping_scale", heldout_damping))
        heldout_gain = tuple(float(v) for v in heldout.get("actuator_gain", heldout_gain))
        eval_seeds = tuple(int(v) for v in heldout.get("seeds", eval_seeds))
        if not heldout_targets or not heldout_damping or not heldout_gain or not eval_seeds:
            raise ValueError("heldout target, dynamics, and seed lists must be non-empty")
        if len(heldout_damping) != len(heldout_gain):
            raise ValueError("heldout damping_scale and actuator_gain must have equal lengths")
    dataset = collect_dataset(
        episodes=train_episodes,
        steps=train_steps,
        target_force_range_n=target_range,
        force_noise_std_n=force_noise_std_n,
        damping_scale=damping_nominal,
        actuator_gain=actuator_nominal,
        friction_scale=friction_nominal,
        actuator_delay_steps=delay_steps,
        kp=controller["kp"], ki=controller["ki"], kd=controller["kd"],
        integral_limit=controller["integral_limit"], control_limit_n=controller["control_limit_n"],
        dynamics_randomization=randomization,
        seed=seed,
    )
    train, test = split_by_episode(dataset, train_fraction=train_fraction)
    policy = ResidualLinearPolicy.fit(train.features, train.targets, ridge=ridge, residual_limit_n=residual_limit)
    rows: list[dict[str, object]] = []
    for target_force_n in heldout_targets:
        for damping_scale, actuator_gain in zip(heldout_damping, heldout_gain):
            for eval_seed in eval_seeds:
                baseline = run(
                    steps=eval_steps,
                    target_force_n=target_force_n,
                    force_noise_std_n=force_noise_std_n,
                    damping_scale=damping_scale,
                    actuator_gain=actuator_gain,
                    friction_scale=friction_nominal,
                    actuator_delay_steps=delay_steps,
                    kp=controller["kp"], ki=controller["ki"], kd=controller["kd"],
                    integral_limit=controller["integral_limit"], control_limit_n=controller["control_limit_n"], seed=eval_seed,
                )
                residual = evaluate_residual(
                    policy,
                    steps=eval_steps,
                    target_force_n=target_force_n,
                    force_noise_std_n=force_noise_std_n,
                    damping_scale=damping_scale,
                    actuator_gain=actuator_gain,
                    friction_scale=friction_nominal,
                    actuator_delay_steps=delay_steps,
                    kp=controller["kp"], ki=controller["ki"], kd=controller["kd"],
                    integral_limit=controller["integral_limit"], control_limit_n=controller["control_limit_n"],
                    seed=eval_seed,
                )
                rows.append({
                    "target_force_n": target_force_n,
                    "damping_scale": damping_scale,
                    "actuator_gain": actuator_gain,
                    "seed": eval_seed,
                    "baseline": asdict(baseline),
                    "residual": asdict(residual),
                })
    rows.append({
        "dataset_rows": len(dataset.features),
        "train_rows": len(train.features),
        "test_rows": len(test.features),
        "test_residual_rmse_n": float(np.sqrt(np.mean((policy.predict(test.features) - test.targets) ** 2))),
    })
    return rows


def run_from_config(config: dict[str, Any], artifact_dir: Path, *, train_episodes: int | None = None,
                    train_steps: int | None = None, eval_steps: int | None = None,
                    seed: int | None = None) -> dict[str, Any]:
    values = _config_values(config)
    learning = config.get("learning", {})
    actual_train_episodes = int(train_episodes if train_episodes is not None else values["episodes"])
    actual_train_steps = int(train_steps if train_steps is not None else values["steps"])
    actual_eval_steps = int(eval_steps if eval_steps is not None else values["eval_steps"])
    actual_seed = int(seed if seed is not None else config.get("experiment", {}).get("seed", 42))
    rows = run_study(train_episodes=actual_train_episodes, train_steps=actual_train_steps,
                     eval_steps=actual_eval_steps, seed=actual_seed, config=config)
    artifact_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": artifact_dir.name, "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config_name": config.get("experiment", {}).get("name"), "config_path": "configs/residual_policy.yaml",
        "git_commit": git_revision(), "python": sys.version, "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "artifact_dir": str(artifact_dir), "seed": actual_seed, "package_snapshot": package_snapshot(),
        "train_episodes": actual_train_episodes, "train_steps": actual_train_steps,
        "eval_steps": actual_eval_steps, "evaluation_rows": len([row for row in rows if "seed" in row]),
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifact_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    (artifact_dir / "results.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "results": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/residual_policy.yaml"))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--train-episodes", type=int)
    parser.add_argument("--train-steps", type=int)
    parser.add_argument("--eval-steps", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output", type=Path, help="deprecated: use --run-id and config artifact_root")
    args = parser.parse_args()
    config = load_config(args.config)
    experiment = config.setdefault("experiment", {})
    run_id = args.run_id or experiment.get("run_id") or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_root = REPOSITORY_ROOT / str(experiment.get("artifact_root", "artifacts/residual-heldout"))
    output = run_from_config(config, artifact_root / str(run_id), train_episodes=args.train_episodes,
                             train_steps=args.train_steps, eval_steps=args.eval_steps, seed=args.seed)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact_root / str(run_id) / "results.json", args.output)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
