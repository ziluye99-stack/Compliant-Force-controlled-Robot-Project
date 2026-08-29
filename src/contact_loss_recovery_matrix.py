"""Run a deterministic MuJoCo contact-loss recovery robustness matrix."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from itertools import product
from pathlib import Path
from typing import Any, Sequence

import yaml

from .contact_loss_recovery import ContactLossRecoveryMetrics, run


DEFAULT_SEPARATION_IMPULSES = (0.2, 0.5, 1.0)
DEFAULT_FORCE_NOISE_STDS = (0.0, 0.1)
DEFAULT_DAMPING_SCALES = (0.5, 1.0, 2.0)
DEFAULT_ACTUATOR_DELAYS = (0, 2)


def _safe_recovery(metrics: ContactLossRecoveryMetrics) -> bool:
    """Require recovery without any explicitly recorded safety violation."""

    return bool(
        metrics.contact_loss_detected
        and metrics.recovery_detected
        and metrics.control_limit_violations == 0
        and metrics.force_limit_violations == 0
        and metrics.safety_gate_activations == 0
    )


def run_matrix(
    *,
    steps: int = 1200,
    target_force_n: float = 5.0,
    disturbance_step: int = 300,
    separation_impulses: Sequence[float] = DEFAULT_SEPARATION_IMPULSES,
    force_noise_stds: Sequence[float] = DEFAULT_FORCE_NOISE_STDS,
    damping_scales: Sequence[float] = DEFAULT_DAMPING_SCALES,
    actuator_delays: Sequence[int] = DEFAULT_ACTUATOR_DELAYS,
    seed: int = 42,
    recovery_fraction: float = 0.9,
    recovery_hold_steps: int = 5,
    loss_threshold_n: float = 0.05,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    control_limit_n: float = 30.0,
    force_limit_n: float = 40.0,
    penetration_limit_m: float = 0.002,
) -> dict[str, object]:
    """Evaluate every mismatch combination using the same episode seed."""

    axes = {
        "separation_impulse_m_s": tuple(float(value) for value in separation_impulses),
        "force_noise_std_n": tuple(float(value) for value in force_noise_stds),
        "damping_scale": tuple(float(value) for value in damping_scales),
        "actuator_delay_steps": tuple(int(value) for value in actuator_delays),
    }
    if any(not values for values in axes.values()):
        raise ValueError("every matrix axis must contain at least one value")

    cases: list[dict[str, object]] = []
    combinations = product(
        axes["separation_impulse_m_s"],
        axes["force_noise_std_n"],
        axes["damping_scale"],
        axes["actuator_delay_steps"],
    )
    for case_index, (impulse, noise, damping, delay) in enumerate(combinations):
        metrics = run(
            steps=steps,
            target_force_n=target_force_n,
            disturbance_step=disturbance_step,
            separation_impulse_m_s=impulse,
            force_noise_std_n=noise,
            damping_scale=damping,
            actuator_delay_steps=delay,
            seed=seed,
            recovery_fraction=recovery_fraction,
            recovery_hold_steps=recovery_hold_steps,
            loss_threshold_n=loss_threshold_n,
            kp=kp,
            ki=ki,
            kd=kd,
            integral_limit=integral_limit,
            control_limit_n=control_limit_n,
            force_limit_n=force_limit_n,
            penetration_limit_m=penetration_limit_m,
        )
        case = asdict(metrics)
        case["case_index"] = case_index
        case["safe_recovery"] = _safe_recovery(metrics)
        cases.append(case)

    safe_count = sum(bool(case["safe_recovery"]) for case in cases)
    return {
        "schema_version": "contact-loss-recovery-matrix/v1",
        "seed": seed,
        "steps": steps,
        "target_force_n": target_force_n,
        "disturbance_step": disturbance_step,
        "recovery_fraction": recovery_fraction,
        "recovery_hold_steps": recovery_hold_steps,
        "loss_threshold_n": loss_threshold_n,
        "controller": {
            "kp": kp,
            "ki": ki,
            "kd": kd,
            "integral_limit": integral_limit,
            "control_limit_n": control_limit_n,
        },
        "safety": {
            "force_limit_n": force_limit_n,
            "penetration_limit_m": penetration_limit_m,
        },
        "axes": {key: list(values) for key, values in axes.items()},
        "case_count": len(cases),
        "safe_recovery_count": safe_count,
        "failure_count": len(cases) - safe_count,
        "cases": cases,
    }


def _mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def run_matrix_from_config(path: Path) -> dict[str, object]:
    """Load the committed YAML contract and execute its matrix."""

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("matrix config must contain a top-level mapping")
    task = _mapping(payload, "task")
    disturbance = _mapping(payload, "disturbance")
    matrix = _mapping(payload, "matrix")
    evaluation = _mapping(payload, "evaluation")
    controller = _mapping(payload, "controller")
    safety = _mapping(payload, "safety")
    result = run_matrix(
        steps=int(task.get("steps", 1200)),
        target_force_n=float(task.get("target_force_n", 5.0)),
        disturbance_step=int(task.get("disturbance_step", disturbance.get("step", 300))),
        separation_impulses=matrix.get("separation_impulse_m_s", DEFAULT_SEPARATION_IMPULSES),
        force_noise_stds=matrix.get("force_noise_std_n", DEFAULT_FORCE_NOISE_STDS),
        damping_scales=matrix.get("damping_scale", DEFAULT_DAMPING_SCALES),
        actuator_delays=matrix.get("actuator_delay_steps", DEFAULT_ACTUATOR_DELAYS),
        seed=int(task.get("seed", 42)),
        recovery_fraction=float(evaluation.get("recovery_fraction", 0.9)),
        recovery_hold_steps=int(evaluation.get("recovery_hold_steps", 5)),
        loss_threshold_n=float(disturbance.get("loss_threshold_n", 0.05)),
        kp=float(controller.get("kp", 0.5)),
        ki=float(controller.get("ki", 5.0)),
        kd=float(controller.get("kd", 0.3)),
        integral_limit=float(controller.get("integral_limit", 10.0)),
        control_limit_n=float(controller.get("control_limit_n", 30.0)),
        force_limit_n=float(safety.get("force_limit_n", 40.0)),
        penetration_limit_m=float(safety.get("penetration_limit_m", 0.002)),
    )
    result["config_path"] = str(path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--target-force", type=float, default=5.0)
    parser.add_argument("--disturbance-step", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = (
        run_matrix_from_config(args.config)
        if args.config
        else run_matrix(
            steps=args.steps,
            target_force_n=args.target_force,
            disturbance_step=args.disturbance_step,
            seed=args.seed,
        )
    )
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
