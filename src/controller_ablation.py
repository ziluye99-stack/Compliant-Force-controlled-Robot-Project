"""Reproducible ablations for residual-policy observations and dynamics."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .contact_force_baseline import run
from .residual_policy import ResidualLinearPolicy, collect_dataset, evaluate_residual, split_by_episode


OBSERVATIONS: dict[str, tuple[int, ...]] = {
    "full": (0, 1, 2, 3, 4),
    "force_error_only": (0,),
    "no_integral": (0, 1, 3, 4),
}
GAINS: dict[str, tuple[float, float, float]] = {
    "nominal": (0.5, 5.0, 0.3),
    "low_integral": (0.5, 2.0, 0.3),
}


def run_ablation(*, train_episodes: int = 6, train_steps: int = 250, eval_steps: int = 400, seed: int = 42) -> list[dict[str, object]]:
    """Train/evaluate a small matrix while holding the task contract fixed."""
    if train_episodes < 2 or train_steps < 10 or eval_steps < 10:
        raise ValueError("at least two training episodes and ten steps are required")
    rows: list[dict[str, object]] = []
    for randomized in (False, True):
        dataset = collect_dataset(
            episodes=train_episodes,
            steps=train_steps,
            target_force_range_n=(3.0, 7.0),
            dynamics_randomization=((1.2, 1.8), (0.7, 0.9)) if randomized else None,
            seed=seed,
        )
        train, test = split_by_episode(dataset)
        for observation_name, feature_indices in OBSERVATIONS.items():
            policy = ResidualLinearPolicy.fit(train.features[:, feature_indices], train.targets)
            prediction = policy.predict(test.features[:, feature_indices])
            for gain_name, (kp, ki, kd) in GAINS.items():
                for eval_seed in (101, 202, 303):
                    baseline = run(
                        steps=eval_steps,
                        target_force_n=5.0,
                        force_noise_std_n=0.2,
                        damping_scale=1.5,
                        actuator_gain=0.8,
                        kp=kp,
                        ki=ki,
                        kd=kd,
                        seed=eval_seed,
                    )
                    residual = evaluate_residual(
                        policy,
                        steps=eval_steps,
                        target_force_n=5.0,
                        force_noise_std_n=0.2,
                        damping_scale=1.5,
                        actuator_gain=0.8,
                        kp=kp,
                        ki=ki,
                        kd=kd,
                        feature_indices=feature_indices,
                        seed=eval_seed,
                    )
                    rows.append({
                        "randomized_training": randomized,
                        "observation": observation_name,
                        "feature_indices": list(feature_indices),
                        "controller_gains": {"kp": kp, "ki": ki, "kd": kd},
                        "gain_variant": gain_name,
                        "seed": eval_seed,
                        "test_residual_rmse_n": float(np.sqrt(np.mean((prediction - test.targets) ** 2))),
                        "baseline": asdict(baseline),
                        "residual": asdict(residual),
                    })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-episodes", type=int, default=6)
    parser.add_argument("--train-steps", type=int, default=250)
    parser.add_argument("--eval-steps", type=int, default=400)
    parser.add_argument("--output", type=Path, default=Path("artifacts/controller-ablation/results.json"))
    args = parser.parse_args()
    rows = run_ablation(train_episodes=args.train_episodes, train_steps=args.train_steps, eval_steps=args.eval_steps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
