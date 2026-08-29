"""MuJoCo normal/tangential contact task with a measurable friction contract."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import mujoco
import numpy as np


MODEL_XML = """
<mujoco model="tangential-contact">
  <option timestep="0.002" gravity="0 0 0"/>
  <worldbody>
    <geom name="plane" type="plane" size="1 1 0.01" friction="0.5 0.01 0.001"/>
    <body name="end_effector" pos="0 0 0.2">
      <joint name="normal_slide" type="slide" axis="0 0 1" damping="1"/>
      <joint name="tangent_slide" type="slide" axis="1 0 0" damping="1"/>
      <geom name="contact_sphere" type="sphere" size="0.05" mass="1" friction="0.5 0.01 0.001"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="normal_motor" joint="normal_slide" gear="1"/>
    <motor name="tangent_motor" joint="tangent_slide" gear="1"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class TangentialContactMetrics:
    target_normal_force_n: float
    target_tangential_force_n: float
    friction_coefficient: float
    mean_normal_force_n: float
    mean_tangential_force_n: float
    tangential_force_rmse_n: float
    max_slip_speed_m_s: float
    mean_slip_speed_m_s: float
    friction_ratio: float
    slipped: bool
    max_penetration_m: float
    contacts_seen: bool


def _contact_forces(model: mujoco.MjModel, data: mujoco.MjData) -> tuple[float, float]:
    contact_force = np.zeros(6, dtype=np.float64)
    normal_force = 0.0
    tangential_force = 0.0
    for contact_id in range(data.ncon):
        mujoco.mj_contactForce(model, data, contact_id, contact_force)
        normal_force += max(0.0, float(contact_force[0]))
        tangential_force += float(np.hypot(contact_force[1], contact_force[2]))
    return normal_force, tangential_force


def run(
    steps: int = 2000,
    target_normal_force_n: float = 5.0,
    target_tangential_force_n: float = 1.0,
    friction_coefficient: float = 0.5,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    normal_control_limit_n: float = 30.0,
    tangential_control_limit_n: float = 10.0,
    seed: int = 42,
) -> TangentialContactMetrics:
    """Run normal-force regulation while applying a tangential force."""
    del seed  # The deterministic scene currently has no stochastic disturbance.
    if steps < 10:
        raise ValueError("steps must be at least 10")
    if target_normal_force_n <= 0 or target_tangential_force_n < 0:
        raise ValueError("target normal force must be positive and tangential force non-negative")
    if friction_coefficient <= 0:
        raise ValueError("friction_coefficient must be positive")
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    model.geom_friction[:, 0] = friction_coefficient
    data = mujoco.MjData(model)
    data.qpos[0] = -0.149
    mujoco.mj_forward(model, data)
    dt = model.opt.timestep
    integral_error = 0.0
    normal_forces: list[float] = []
    tangential_forces: list[float] = []
    slip_speeds: list[float] = []
    penetrations: list[float] = []
    for _ in range(steps):
        normal_force_n, tangential_force_n = _contact_forces(model, data)
        error = target_normal_force_n - normal_force_n
        integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
        normal_control = -(kp * error + ki * integral_error + kd * float(data.qvel[0]))
        normal_control = float(np.clip(normal_control, -normal_control_limit_n, normal_control_limit_n))
        # A positive x command creates an opposing tangential friction force.
        tangent_control = float(np.clip(target_tangential_force_n, 0.0, tangential_control_limit_n))
        data.ctrl[0] = normal_control
        data.ctrl[1] = tangent_control
        mujoco.mj_step(model, data)
        normal_forces.append(normal_force_n)
        tangential_forces.append(tangential_force_n)
        slip_speeds.append(abs(float(data.qvel[1])))
        penetrations.append(max(0.0, float(-(data.qpos[0] + 0.15))))
    tail_start = max(0, int(steps * 0.8))
    normal_tail = np.asarray(normal_forces[tail_start:], dtype=np.float64)
    tangent_tail = np.asarray(tangential_forces[tail_start:], dtype=np.float64)
    slip_tail = np.asarray(slip_speeds[tail_start:], dtype=np.float64)
    mean_normal = float(normal_tail.mean())
    mean_tangent = float(tangent_tail.mean())
    return TangentialContactMetrics(
        target_normal_force_n=target_normal_force_n,
        target_tangential_force_n=target_tangential_force_n,
        friction_coefficient=friction_coefficient,
        mean_normal_force_n=mean_normal,
        mean_tangential_force_n=mean_tangent,
        tangential_force_rmse_n=float(np.sqrt(np.mean((tangent_tail - target_tangential_force_n) ** 2))),
        max_slip_speed_m_s=float(slip_tail.max()),
        mean_slip_speed_m_s=float(slip_tail.mean()),
        friction_ratio=float(mean_tangent / mean_normal) if mean_normal > 0 else float("inf"),
        # Treat sub-centimeter-per-second solver drift as sticking; retain the
        # raw speed metrics so the threshold remains auditable.
        slipped=bool(slip_tail.max() > 1e-2),
        max_penetration_m=float(max(penetrations)),
        contacts_seen=bool(np.any(np.asarray(normal_forces) > 0)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--target-normal", type=float, default=5.0)
    parser.add_argument("--target-tangential", type=float, default=1.0)
    parser.add_argument("--friction", type=float, default=0.5)
    args = parser.parse_args()
    print(json.dumps(run(
        steps=args.steps,
        target_normal_force_n=args.target_normal,
        target_tangential_force_n=args.target_tangential,
        friction_coefficient=args.friction,
    ).__dict__, indent=2))


if __name__ == "__main__":
    main()
