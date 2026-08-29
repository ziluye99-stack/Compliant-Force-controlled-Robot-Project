"""Deterministic MuJoCo normal-contact force tracking baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import mujoco
import numpy as np


MODEL_XML = """
<mujoco model="normal-force-baseline">
  <option timestep="0.002" gravity="0 0 0"/>
  <worldbody>
    <geom name="wall" type="plane" size="1 1 0.01"/>
    <body name="end_effector" pos="0 0 0.2">
      <joint name="normal_slide" type="slide" axis="0 0 1" damping="1"/>
      <geom name="contact_sphere" type="sphere" size="0.05" mass="1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="normal_motor" joint="normal_slide" gear="1"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class ForceTrackingMetrics:
    target_force_n: float
    mean_force_n: float
    force_rmse_n: float
    force_std_n: float
    measured_force_rmse_n: float
    measured_force_std_n: float
    max_abs_control_n: float
    max_penetration_m: float
    contacts_seen: bool


def _normal_force(model: mujoco.MjModel, data: mujoco.MjData) -> float:
    contact_force = np.zeros(6, dtype=np.float64)
    total = 0.0
    for contact_id in range(data.ncon):
        mujoco.mj_contactForce(model, data, contact_id, contact_force)
        total += max(0.0, float(contact_force[0]))
    return total


def run(
    steps: int = 2000,
    target_force_n: float = 5.0,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    control_limit_n: float = 30.0,
    force_noise_std_n: float = 0.0,
    damping_scale: float = 1.0,
    actuator_gain: float = 1.0,
    seed: int = 42,
) -> ForceTrackingMetrics:
    """Run the baseline with optional sensor noise and dynamics mismatch."""
    if steps < 10:
        raise ValueError("steps must be at least 10")
    if target_force_n <= 0:
        raise ValueError("target_force_n must be positive")
    if force_noise_std_n < 0:
        raise ValueError("force_noise_std_n must be non-negative")
    if damping_scale <= 0 or actuator_gain <= 0:
        raise ValueError("damping_scale and actuator_gain must be positive")
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    model.dof_damping[0] *= damping_scale
    model.actuator_gear[0, 0] *= actuator_gain
    data = mujoco.MjData(model)
    # Start just above the plane: body origin 0.2 m minus sphere radius 0.05 m.
    data.qpos[0] = -0.149
    mujoco.mj_forward(model, data)

    dt = model.opt.timestep
    integral_error = 0.0
    forces: list[float] = []
    measured_forces: list[float] = []
    controls: list[float] = []
    penetrations: list[float] = []
    for _ in range(steps):
        force_n = _normal_force(model, data)
        measured_force_n = max(0.0, force_n + float(rng.normal(0.0, force_noise_std_n)))
        error = target_force_n - measured_force_n
        integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
        control = -(kp * error + ki * integral_error + kd * float(data.qvel[0]))
        control = float(np.clip(control, -control_limit_n, control_limit_n))
        data.ctrl[0] = control
        mujoco.mj_step(model, data)
        forces.append(force_n)
        measured_forces.append(measured_force_n)
        controls.append(control)
        penetrations.append(max(0.0, float(-(data.qpos[0] + 0.15))))

    tail = np.asarray(forces[max(0, int(steps * 0.8)) :], dtype=np.float64)
    measured_tail = np.asarray(measured_forces[max(0, int(steps * 0.8)) :], dtype=np.float64)
    return ForceTrackingMetrics(
        target_force_n=target_force_n,
        mean_force_n=float(tail.mean()),
        force_rmse_n=float(np.sqrt(np.mean((tail - target_force_n) ** 2))),
        force_std_n=float(tail.std()),
        measured_force_rmse_n=float(np.sqrt(np.mean((measured_tail - target_force_n) ** 2))),
        measured_force_std_n=float(measured_tail.std()),
        max_abs_control_n=float(np.max(np.abs(controls))),
        max_penetration_m=float(max(penetrations)),
        contacts_seen=bool(np.any(np.asarray(forces) > 0)),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--target-force", type=float, default=5.0)
    parser.add_argument("--noise-std", type=float, default=0.0)
    parser.add_argument("--damping-scale", type=float, default=1.0)
    parser.add_argument("--actuator-gain", type=float, default=1.0)
    args = parser.parse_args()
    metrics = run(
        steps=args.steps,
        target_force_n=args.target_force,
        force_noise_std_n=args.noise_std,
        damping_scale=args.damping_scale,
        actuator_gain=args.actuator_gain,
    )
    print(json.dumps(metrics.__dict__, indent=2))


if __name__ == "__main__":
    main()
