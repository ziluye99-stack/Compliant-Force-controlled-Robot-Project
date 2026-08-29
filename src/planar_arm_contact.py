"""Platform-neutral two-link arm contact task with Jacobian-transpose force control."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import mujoco
import numpy as np


MODEL_XML = """
<mujoco model="planar-arm-contact">
  <option timestep="0.002" gravity="0 0 0"/>
  <worldbody>
    <geom name="plane" type="plane" size="1 1 0.01" friction="0.5 0.01 0.001"/>
    <body name="upper_arm" pos="0 0 0.35">
      <joint name="shoulder" type="hinge" axis="0 1 0" damping="0.4"/>
      <geom name="upper_link" type="capsule" fromto="0 0 0 0.22 0 0" size="0.035" mass="0.5"/>
      <body name="forearm" pos="0.22 0 0">
        <joint name="elbow" type="hinge" axis="0 1 0" damping="0.4"/>
        <geom name="lower_link" type="capsule" fromto="0 0 0 0.20 0 0" size="0.03" mass="0.4"/>
        <geom name="contact_sphere" type="sphere" pos="0.20 0 0" size="0.04" mass="0.1" friction="0.5 0.01 0.001"/>
        <site name="tcp" pos="0.20 0 0" size="0.008" rgba="0 1 0 1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="shoulder_motor" joint="shoulder" gear="1"/>
    <motor name="elbow_motor" joint="elbow" gear="1"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class PlanarArmContactMetrics:
    target_normal_force_n: float
    target_tangential_force_n: float
    friction_coefficient: float
    mean_normal_force_n: float
    mean_tangential_force_n: float
    max_position_error_m: float
    mean_tcp_x_m: float
    max_joint_torque_nm: float
    max_penetration_m: float
    contacts_seen: bool


def _contact_forces(model: mujoco.MjModel, data: mujoco.MjData) -> tuple[float, float]:
    wrench = np.zeros(6, dtype=np.float64)
    normal = 0.0
    tangent = 0.0
    for contact_id in range(data.ncon):
        mujoco.mj_contactForce(model, data, contact_id, wrench)
        normal += max(0.0, float(wrench[0]))
        tangent += float(np.hypot(wrench[1], wrench[2]))
    return normal, tangent


def _make_system(friction_coefficient: float) -> tuple[mujoco.MjModel, mujoco.MjData, int]:
    if friction_coefficient <= 0:
        raise ValueError("friction_coefficient must be positive")
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    model.geom_friction[:, 0] = friction_coefficient
    data = mujoco.MjData(model)
    # This configuration places the spherical TCP just in contact with z=0.
    data.qpos[0] = 0.98
    data.qpos[1] = -0.30
    mujoco.mj_forward(model, data)
    return model, data, model.site("tcp").id


def run(
    steps: int = 2000,
    target_normal_force_n: float = 5.0,
    target_tangential_force_n: float = 1.0,
    friction_coefficient: float = 0.5,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    force_limit_n: float = 30.0,
    torque_limit_nm: float = 20.0,
) -> PlanarArmContactMetrics:
    """Apply a Cartesian force through a two-joint arm using J^T mapping."""
    if steps < 10:
        raise ValueError("steps must be at least 10")
    if target_normal_force_n <= 0 or target_tangential_force_n < 0:
        raise ValueError("target normal force must be positive and tangential force non-negative")
    model, data, tcp_id = _make_system(friction_coefficient)
    dt = model.opt.timestep
    integral_error = 0.0
    normal_forces: list[float] = []
    tangent_forces: list[float] = []
    tcp_x_positions: list[float] = []
    position_errors: list[float] = []
    joint_torques: list[float] = []
    penetrations: list[float] = []
    target_tcp_x = float(data.site_xpos[tcp_id][0])
    for _ in range(steps):
        normal_force_n, tangential_force_n = _contact_forces(model, data)
        error = target_normal_force_n - normal_force_n
        integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
        normal_effort = float(np.clip(kp * error + ki * integral_error - kd * data.qvel[0], -force_limit_n, force_limit_n))
        desired_force = np.asarray([target_tangential_force_n, 0.0, -normal_effort], dtype=np.float64)
        jacp = np.zeros((3, model.nv), dtype=np.float64)
        jacr = np.zeros((3, model.nv), dtype=np.float64)
        mujoco.mj_jacSite(model, data, jacp, jacr, tcp_id)
        torque = jacp.T @ desired_force
        torque = np.clip(torque, -torque_limit_nm, torque_limit_nm)
        data.ctrl[:] = torque
        mujoco.mj_step(model, data)
        tcp_x = float(data.site_xpos[tcp_id][0])
        normal_forces.append(normal_force_n)
        tangent_forces.append(tangential_force_n)
        tcp_x_positions.append(tcp_x)
        position_errors.append(abs(tcp_x - target_tcp_x))
        joint_torques.append(float(np.max(np.abs(torque))))
        penetrations.append(max(0.0, float(-(data.site_xpos[tcp_id][2] - 0.04))))
    tail_start = max(0, int(steps * 0.8))
    normal_tail = np.asarray(normal_forces[tail_start:], dtype=np.float64)
    tangent_tail = np.asarray(tangent_forces[tail_start:], dtype=np.float64)
    tcp_tail = np.asarray(tcp_x_positions[tail_start:], dtype=np.float64)
    return PlanarArmContactMetrics(
        target_normal_force_n=target_normal_force_n,
        target_tangential_force_n=target_tangential_force_n,
        friction_coefficient=friction_coefficient,
        mean_normal_force_n=float(normal_tail.mean()),
        mean_tangential_force_n=float(tangent_tail.mean()),
        max_position_error_m=float(max(position_errors)),
        mean_tcp_x_m=float(tcp_tail.mean()),
        max_joint_torque_nm=float(max(joint_torques)),
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
