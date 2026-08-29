"""Summarize two-rate matrix results with deterministic bootstrap intervals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


METRICS = (
    "force_rmse_n",
    "measured_force_rmse_n",
    "tail_abs_error_n",
    "max_penetration_m",
    "peak_force_n",
    "contact_loss_rate",
    "max_abs_control_n",
    "safety_gate_activations",
)


def bootstrap_mean_ci(values: list[float], *, replicates: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Return a percentile bootstrap CI for a mean, including the n=1 case."""
    if not values or replicates < 1:
        raise ValueError("values must be non-empty and replicates must be positive")
    array = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError("metric values must be finite")
    if len(array) == 1:
        value = float(array[0])
        return value, value
    rng = np.random.default_rng(seed)
    samples = rng.choice(array, size=(replicates, len(array)), replace=True).mean(axis=1)
    low, high = np.percentile(samples, [2.5, 97.5])
    return float(low), float(high)


def _metric_value(result: dict[str, Any], variant: str, metric: str) -> float:
    key = "baseline" if variant == "pi_only" else "residual"
    metrics = result.get(key)
    if not isinstance(metrics, dict) or metric not in metrics:
        raise ValueError(f"missing {key}.{metric} for {variant}")
    return float(metrics[metric])


def summarize_rows(rows: list[dict[str, Any]], *, replicates: int = 2000, seed: int = 0) -> dict[str, Any]:
    """Aggregate one matrix result list and paired residual-vs-PI deltas."""
    if not rows:
        raise ValueError("results must contain at least one row")
    by_variant: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        case = row.get("case", {})
        variant = str(case.get("variant", ""))
        if not variant:
            raise ValueError("each result row must contain case.variant")
        by_variant.setdefault(variant, []).append(row.get("result", {}))

    summary: dict[str, Any] = {"case_count": len(rows), "variants": {}}
    for variant, variant_rows in sorted(by_variant.items()):
        metrics: dict[str, Any] = {}
        for metric in METRICS:
            values = [_metric_value(result, variant, metric) for result in variant_rows]
            ci = bootstrap_mean_ci(values, replicates=replicates, seed=seed + len(metrics))
            metrics[metric] = {
                "n": len(values),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "bootstrap_95ci": list(ci),
            }
        summary["variants"][variant] = metrics

    baseline_rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        case = row.get("case", {})
        key = tuple(sorted((name, value) for name, value in case.items() if name != "variant"))
        baseline_rows[key] = row.get("result", {}).get("baseline", {})
    deltas: dict[str, Any] = {}
    for variant, variant_rows in sorted(by_variant.items()):
        if variant == "pi_only":
            continue
        paired: dict[str, list[float]] = {metric: [] for metric in METRICS}
        for row in rows:
            case = row.get("case", {})
            if case.get("variant") != variant:
                continue
            key = tuple(sorted((name, value) for name, value in case.items() if name != "variant"))
            baseline = baseline_rows.get(key)
            result = row.get("result", {}).get("residual", {})
            if not isinstance(baseline, dict):
                raise ValueError(f"missing paired PI baseline for case {case}")
            for metric in METRICS:
                paired[metric].append(float(result[metric]) - float(baseline[metric]))
        deltas[variant] = {}
        for index, (metric, values) in enumerate(paired.items()):
            ci = bootstrap_mean_ci(values, replicates=replicates, seed=seed + 100 + index)
            deltas[variant][metric] = {
                "n": len(values),
                "mean_delta": float(np.mean(values)),
                "std_delta": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "bootstrap_95ci": list(ci),
            }
    summary["paired_delta_residual_minus_pi"] = deltas
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replicates", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    payload = json.loads(args.results.read_text(encoding="utf-8"))
    rows = payload.get("results") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("results file must be a list or matrix-run output object")
    summary = summarize_rows(rows, replicates=args.replicates, seed=args.seed)
    encoded = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
