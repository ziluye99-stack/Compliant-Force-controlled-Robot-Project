"""Held-out target-force and dynamics study for the residual baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .contact_force_baseline import run
from .residual_policy import ResidualLinearPolicy, collect_dataset, evaluate_residual, split_by_episode


def run_study(
    *,
    train_episodes: int = 12,
    train_steps: int = 500,
    eval_steps: int = 1000,
    seed: int = 42,
) -> list[dict[str, object]]:
    """Train on a target range and evaluate held-out target/dynamics settings."""
    dataset = collect_dataset(
        episodes=train_episodes,
        steps=train_steps,
        target_force_range_n=(3.0, 7.0),
        seed=seed,
    )
    train, test = split_by_episode(dataset)
    policy = ResidualLinearPolicy.fit(train.features, train.targets)
    rows: list[dict[str, object]] = []
    for target_force_n in (4.0, 6.0):
        for damping_scale, actuator_gain in ((1.2, 0.9), (1.8, 0.7)):
            for eval_seed in (101, 202, 303):
                baseline = run(
                    steps=eval_steps,
                    target_force_n=target_force_n,
                    force_noise_std_n=0.2,
                    damping_scale=damping_scale,
                    actuator_gain=actuator_gain,
                    seed=eval_seed,
                )
                residual = evaluate_residual(
                    policy,
                    steps=eval_steps,
                    target_force_n=target_force_n,
                    force_noise_std_n=0.2,
                    damping_scale=damping_scale,
                    actuator_gain=actuator_gain,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-episodes", type=int, default=12)
    parser.add_argument("--train-steps", type=int, default=500)
    parser.add_argument("--eval-steps", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("artifacts/residual-heldout/results.json"))
    args = parser.parse_args()
    rows = run_study(
        train_episodes=args.train_episodes,
        train_steps=args.train_steps,
        eval_steps=args.eval_steps,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
