"""Run the YAML-defined two-rate residual force-control evaluation matrix.

This is a simulation-only batch entry point.  It writes provenance and
results incrementally so an interrupted local run leaves an inspectable
partial artifact.  It never submits jobs, selects GPUs, or sends hardware
commands.
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

from .experiment import interface_contract_summary, load_config, package_snapshot
from .two_rate_residual import VARIANTS, train_and_evaluate


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _as_list(mapping: dict[str, Any], key: str, default: float | int) -> list[float | int]:
    value = mapping.get(key, [default])
    if isinstance(value, (float, int)):
        return [value]
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty scalar or list")
    return value


def _positive(value: float | int, name: str) -> float | int:
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def matrix_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand the configured Cartesian product into stable, serializable cases."""
    variants = config.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants must be a non-empty list")
    unknown = set(variants) - set(VARIANTS)
    if unknown:
        raise ValueError(f"unknown variants: {sorted(unknown)}")

    training = config.get("training", {})
    evaluation = config.get("evaluation", {})
    if not isinstance(training, dict) or not isinstance(evaluation, dict):
        raise ValueError("training and evaluation must be mappings")
    targets = _as_list(evaluation, "target_force_n", 5.0)
    seeds = _as_list(training, "seeds", 42)
    heldout = evaluation.get("heldout_dynamics", {})
    if not isinstance(heldout, dict):
        raise ValueError("evaluation.heldout_dynamics must be a mapping")
    friction = _as_list(heldout, "friction_scale", 1.0)
    stiffness = _as_list(heldout, "stiffness_scale", 1.0)
    noise = _as_list(heldout, "force_noise_std_n", 0.0)
    delay = _as_list(heldout, "actuator_delay_steps", 0)
    cases: list[dict[str, Any]] = []
    for variant, target, seed, friction_scale, stiffness_scale, noise_std, delay_steps in itertools.product(
        variants, targets, seeds, friction, stiffness, noise, delay
    ):
        cases.append({
            "variant": str(variant),
            "target_force_n": float(_positive(float(target), "target_force_n")),
            "seed": int(seed),
            "friction_scale": float(_positive(float(friction_scale), "friction_scale")),
            "stiffness_scale": float(_positive(float(stiffness_scale), "stiffness_scale")),
            "force_noise_std_n": float(_positive(float(noise_std), "force_noise_std_n"))
            if float(noise_std) > 0 else 0.0,
            "actuator_delay_steps": int(delay_steps),
        })
    return cases


def _git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, check=False,
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _training_values(
    config: dict[str, Any],
) -> tuple[tuple[float, float], dict[str, float], dict[str, tuple[float, float]]]:
    training = config["training"]
    target_range = tuple(float(v) for v in training.get("target_force_range_n", (3.0, 7.0)))
    if len(target_range) != 2 or target_range[0] <= 0 or target_range[1] < target_range[0]:
        raise ValueError("training.target_force_range_n must be an ordered positive pair")
    dynamics = training.get("dynamics", {})
    nominal = dynamics.get("nominal", {}) if isinstance(dynamics, dict) else {}
    if not isinstance(nominal, dict):
        raise ValueError("training.dynamics.nominal must be a mapping")
    values = {
        "damping_scale": float(nominal.get("damping_scale", 1.5)),
        "actuator_gain": float(nominal.get("actuator_gain", 0.8)),
        "friction_scale": float(nominal.get("friction_scale", 1.0)),
        "stiffness_scale": float(nominal.get("stiffness_scale", 1.0)),
    }
    for name, value in values.items():
        _positive(value, f"training.dynamics.nominal.{name}")
    randomized_raw = dynamics.get("randomized", {}) if isinstance(dynamics, dict) else {}
    if not isinstance(randomized_raw, dict):
        raise ValueError("training.dynamics.randomized must be a mapping")
    randomized: dict[str, tuple[float, float]] = {}
    for name, bounds in randomized_raw.items():
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            raise ValueError(f"training.dynamics.randomized.{name} must be a two-value list")
        randomized[name] = (float(bounds[0]), float(bounds[1]))
    return target_range, values, randomized


def run_matrix(
    config: dict[str, Any],
    artifact_dir: Path,
    *,
    max_cases: int | None = None,
    dry_run: bool = False,
    episodes: int | None = None,
    steps: int | None = None,
    eval_steps: int | None = None,
) -> dict[str, Any]:
    """Run cases and return the manifest plus result rows."""
    cases = matrix_cases(config)
    if max_cases is not None:
        if max_cases < 1:
            raise ValueError("max_cases must be positive")
        cases = cases[:max_cases]
    target_range, train_dynamics, train_randomization = _training_values(config)
    control = config.get("control", {})
    training = config.get("training", {})
    evaluation = config.get("evaluation", {})
    interface = interface_contract_summary(config)
    period = int(control.get("residual_period_fast_steps", 25))
    train_episodes = int(episodes if episodes is not None else training.get("episodes", 4))
    train_steps = int(steps if steps is not None else training.get("steps_per_episode", 500))
    run_steps = int(eval_steps if eval_steps is not None else evaluation.get("steps", 200))
    if train_episodes < 1 or train_steps < 10 or run_steps < 10:
        raise ValueError("episodes and step counts must be positive; steps must be at least 10")

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
        "training": {
            "episodes": train_episodes,
            "steps_per_episode": train_steps,
            "target_force_range_n": list(target_range),
            "nominal_dynamics": train_dynamics,
            "randomized_dynamics": train_randomization,
        },
        "evaluation": {"steps": run_steps, "residual_period_fast_steps": period},
        "package_snapshot": package_snapshot(),
        "interface_contract": interface,
    }
    if dry_run:
        return {"manifest": manifest, "cases": cases}

    artifact_dir.mkdir(parents=True, exist_ok=False)
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (artifact_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    results: list[dict[str, Any]] = []
    results_path = artifact_dir / "results.json"
    for index, case in enumerate(cases):
        result = train_and_evaluate(
            case["variant"],
            episodes=train_episodes,
            steps=train_steps,
            eval_steps=run_steps,
            residual_period_fast_steps=period,
            seed=case["seed"],
            target_force_range_n=target_range,
            train_damping_scale=train_dynamics["damping_scale"],
            train_actuator_gain=train_dynamics["actuator_gain"],
            train_friction_scale=train_dynamics["friction_scale"],
            train_stiffness_scale=train_dynamics["stiffness_scale"],
            train_dynamics_randomization=train_randomization,
            eval_target_force_n=case["target_force_n"],
            eval_force_noise_std_n=case["force_noise_std_n"],
            eval_damping_scale=train_dynamics["damping_scale"],
            eval_actuator_gain=train_dynamics["actuator_gain"],
            eval_friction_scale=case["friction_scale"],
            eval_stiffness_scale=case["stiffness_scale"],
            eval_actuator_delay_steps=case["actuator_delay_steps"],
        )
        results.append({"index": index, "case": case, "result": result})
        results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return {"manifest": manifest, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/two_rate_residual.yaml"))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--episodes", type=int)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--eval-steps", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    experiment = config.get("experiment", {})
    run_id = args.run_id or experiment.get("run_id") or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_dir = REPOSITORY_ROOT / str(experiment.get("artifact_root", "artifacts/two-rate-residual")) / str(run_id)
    output = run_matrix(
        config, artifact_dir, max_cases=args.max_cases, dry_run=args.dry_run,
        episodes=args.episodes, steps=args.steps, eval_steps=args.eval_steps,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
