"""Deterministic MuJoCo contact-loss and recovery experiment."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import mujoco
import numpy as np

from .contact_force_baseline import MODEL_XML, _normal_force


@dataclass(frozen=True)
class ContactLossRecoveryMetrics:
    target_force_n: float
    disturbance_step: int
    separation_impulse_m_s: float
    contact_loss_step: int | None
    recovery_step: int | None
    loss_duration_steps: int | None
    recovery_time_s: float | None
    pre_disturbance_force_n: float
    recovery_force_n: float | None
    peak_force_after_disturbance_n: float
    max_abs_control_n: float
    max_penetration_m: float
    control_limit_violations: int
    force_limit_violations: int
    safety_gate_activations: int
    contact_loss_detected: bool
    recovery_detected: bool
    contacts_seen: bool


def _first_recovery_step(
    forces: np.ndarray,
    loss_step: int,
    target_force_n: float,
    recovery_fraction: float,
    recovery_hold_steps: int,
) -> int | None:
    threshold = target_force_n * recovery_fraction
    last_start = len(forces) - recovery_hold_steps + 1
    for start in range(loss_step + 1, max(loss_step + 1, last_start)):
        if np.all(forces[start : start + recovery_hold_steps] >= threshold):
            return start
    return None


def run(
    steps: int = 1200,
    target_force_n: float = 5.0,
    disturbance_step: int = 300,
    separation_impulse_m_s: float = 0.2,
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
) -> ContactLossRecoveryMetrics:
    """Apply one outward impulse and measure whether bounded force control recovers."""
    if steps < 50:
        raise ValueError("steps must be at least 50")
    if target_force_n <= 0:
        raise ValueError("target_force_n must be positive")
    if not 10 <= disturbance_step < steps - 10:
        raise ValueError("disturbance_step must leave room before and after the disturbance")
    if separation_impulse_m_s < 0:
        raise ValueError("separation_impulse_m_s must be non-negative")
    if not 0 < recovery_fraction <= 1:
        raise ValueError("recovery_fraction must be in (0, 1]")
    if recovery_hold_steps < 1:
        raise ValueError("recovery_hold_steps must be positive")
    if loss_threshold_n < 0 or control_limit_n <= 0 or force_limit_n <= 0 or penetration_limit_m < 0:
        raise ValueError("thresholds and limits must be non-negative, with positive force limits")

    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    data = mujoco.MjData(model)
    data.qpos[0] = -0.149
    mujoco.mj_forward(model, data)

    dt = float(model.opt.timestep)
    integral_error = 0.0
    forces: list[float] = []
    controls: list[float] = []
    penetrations: list[float] = []
    control_limit_violations = 0
    force_limit_violations = 0
    safety_gate_activations = 0

    for step in range(steps):
        if step == disturbance_step:
            # This is a synthetic, logged disturbance; no hardware command is involved.
            data.qvel[0] += separation_impulse_m_s
        force_n = _normal_force(model, data)
        error = target_force_n - force_n
        integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
        raw_control = -(kp * error + ki * integral_error + kd * float(data.qvel[0]))
        control = float(np.clip(raw_control, -control_limit_n, control_limit_n))
        control_limit_violations += int(abs(raw_control) > control_limit_n)
        force_limit_violations += int(force_n > force_limit_n)
        data.ctrl[0] = control
        mujoco.mj_step(model, data)
        penetration_m = max(0.0, float(-(data.qpos[0] + 0.15)))
        if not np.isfinite(force_n) or not np.isfinite(control) or penetration_m > penetration_limit_m:
            safety_gate_activations += 1
        forces.append(force_n)
        controls.append(control)
        penetrations.append(penetration_m)

    force_array = np.asarray(forces, dtype=np.float64)
    post_disturbance = force_array[disturbance_step:]
    loss_indices = np.flatnonzero(post_disturbance <= loss_threshold_n)
    loss_step = int(disturbance_step + loss_indices[0]) if loss_indices.size else None
    recovery_step = (
        _first_recovery_step(
            force_array,
            loss_step,
            target_force_n,
            recovery_fraction,
            recovery_hold_steps,
        )
        if loss_step is not None
        else None
    )
    pre_start = max(0, disturbance_step - 20)
    pre_disturbance_force = float(np.mean(force_array[pre_start:disturbance_step]))
    recovery_force = float(force_array[recovery_step]) if recovery_step is not None else None
    return ContactLossRecoveryMetrics(
        target_force_n=target_force_n,
        disturbance_step=disturbance_step,
        separation_impulse_m_s=separation_impulse_m_s,
        contact_loss_step=loss_step,
        recovery_step=recovery_step,
        loss_duration_steps=(recovery_step - loss_step if recovery_step is not None and loss_step is not None else None),
        recovery_time_s=(recovery_step - loss_step) * dt if recovery_step is not None and loss_step is not None else None,
        pre_disturbance_force_n=pre_disturbance_force,
        recovery_force_n=recovery_force,
        peak_force_after_disturbance_n=float(np.max(post_disturbance)),
        max_abs_control_n=float(np.max(np.abs(np.asarray(controls, dtype=np.float64)))),
        max_penetration_m=float(np.max(np.asarray(penetrations, dtype=np.float64))),
        control_limit_violations=control_limit_violations,
        force_limit_violations=force_limit_violations,
        safety_gate_activations=safety_gate_activations,
        contact_loss_detected=loss_step is not None,
        recovery_detected=recovery_step is not None,
        contacts_seen=bool(np.any(force_array > loss_threshold_n)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--target-force", type=float, default=5.0)
    parser.add_argument("--disturbance-step", type=int, default=300)
    parser.add_argument("--separation-impulse", type=float, default=0.2)
    parser.add_argument("--recovery-fraction", type=float, default=0.9)
    parser.add_argument("--recovery-hold-steps", type=int, default=5)
    parser.add_argument("--loss-threshold", type=float, default=0.05)
    args = parser.parse_args()
    metrics = run(
        steps=args.steps,
        target_force_n=args.target_force,
        disturbance_step=args.disturbance_step,
        separation_impulse_m_s=args.separation_impulse,
        recovery_fraction=args.recovery_fraction,
        recovery_hold_steps=args.recovery_hold_steps,
        loss_threshold_n=args.loss_threshold,
    )
    print(json.dumps(metrics.__dict__, indent=2))


if __name__ == "__main__":
    main()
