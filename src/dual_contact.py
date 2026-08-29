"""Deterministic platform-neutral MuJoCo dual-contact force-control fixture.

The tool has two actuated translational degrees of freedom.  One spherical pad
pushes on a horizontal plane and the other pushes on a vertical plane.  The
fixture is intentionally not a robot model: it isolates simultaneous contact
force regulation and safety metrics before a selected arm or humanoid model is
introduced.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import mujoco
import numpy as np


MODEL_XML = """
<mujoco model="dual-contact-fixture">
  <option timestep="0.002" gravity="0 0 0" integrator="implicitfast"/>
  <size njmax="200" nconmax="100"/>
  <worldbody>
    <geom name="floor" type="plane" pos="0 0 0" size="1 1 0.01"
      friction="0.6 0.01 0.001" solref="0.01 1"/>
    <geom name="wall" type="plane" pos="0 0 0" quat="0.70710678 0 0.70710678 0" size="1 1 0.01"
      friction="0.6 0.01 0.001" solref="0.01 1"/>
    <body name="tool" pos="0.10 0 0.10">
      <joint name="floor_slide" type="slide" axis="0 0 1" damping="2" armature="0.01"/>
      <joint name="wall_slide" type="slide" axis="1 0 0" damping="2" armature="0.01"/>
      <geom name="floor_pad" type="sphere" pos="0 0 -0.05" size="0.05" mass="1"
        friction="0.6 0.01 0.001"/>
      <geom name="wall_pad" type="sphere" pos="-0.05 0 0" size="0.05" mass="1"
        friction="0.6 0.01 0.001"/>
      <site name="floor_tcp" pos="0 0 -0.05" size="0.006" rgba="0 1 0 1"/>
      <site name="wall_tcp" pos="-0.05 0 0" size="0.006" rgba="1 0 0 1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="floor_motor" joint="floor_slide" gear="1"/>
    <motor name="wall_motor" joint="wall_slide" gear="1"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class DualContactMetrics:
    target_floor_force_n: float
    target_wall_force_n: float
    mean_floor_force_n: float
    mean_wall_force_n: float
    floor_force_rmse_n: float
    wall_force_rmse_n: float
    max_floor_penetration_m: float
    max_wall_penetration_m: float
    peak_total_force_n: float
    max_control_n: float
    control_limit_violations: int
    force_limit_violations: int
    floor_contact_loss_rate: float
    wall_contact_loss_rate: float
    contacts_seen: bool


def _make_system() -> tuple[mujoco.MjModel, mujoco.MjData, int, int]:
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    data = mujoco.MjData(model)
    # The pad centers start exactly at both surfaces; the controller supplies
    # the inward effort and the solver generates the contact reaction.
    data.qpos[:] = 0.0
    mujoco.mj_forward(model, data)
    return model, data, model.geom("floor_pad").id, model.geom("wall_pad").id


def _pad_force(model: mujoco.MjModel, data: mujoco.MjData, pad_id: int) -> float:
    wrench = np.zeros(6, dtype=np.float64)
    force = 0.0
    for contact_id in range(data.ncon):
        contact = data.contact[contact_id]
        if int(contact.geom1) != pad_id and int(contact.geom2) != pad_id:
            continue
        mujoco.mj_contactForce(model, data, contact_id, wrench)
        force += abs(float(wrench[0]))
    return force


def run(
    steps: int = 1500,
    target_floor_force_n: float = 5.0,
    target_wall_force_n: float = 4.0,
    kp: float = 0.8,
    ki: float = 7.0,
    kd: float = 0.5,
    integral_limit: float = 5.0,
    control_limit_n: float = 30.0,
    force_limit_n: float = 40.0,
    seed: int = 42,
) -> DualContactMetrics:
    """Regulate both contact forces and return auditable safety metrics."""
    del seed  # The fixture is deterministic; the argument keeps the run contract uniform.
    if steps < 20:
        raise ValueError("steps must be at least 20")
    if target_floor_force_n <= 0 or target_wall_force_n <= 0:
        raise ValueError("both target forces must be positive")
    if control_limit_n <= 0 or force_limit_n <= 0:
        raise ValueError("force limits must be positive")

    model, data, floor_pad_id, wall_pad_id = _make_system()
    pad_radius = float(model.geom_size[floor_pad_id][0])
    dt = model.opt.timestep
    integral = np.zeros(2, dtype=np.float64)
    floor_forces: list[float] = []
    wall_forces: list[float] = []
    floor_penetrations: list[float] = []
    wall_penetrations: list[float] = []
    controls: list[float] = []
    control_limit_violations = 0
    force_limit_violations = 0

    for _ in range(steps):
        floor_force = _pad_force(model, data, floor_pad_id)
        wall_force = _pad_force(model, data, wall_pad_id)
        measured = np.asarray([floor_force, wall_force], dtype=np.float64)
        target = np.asarray([target_floor_force_n, target_wall_force_n], dtype=np.float64)
        error = target - measured
        integral = np.clip(integral + error * dt, -integral_limit, integral_limit)
        velocity = np.asarray([data.qvel[0], data.qvel[1]], dtype=np.float64)
        effort = kp * error + ki * integral - kd * velocity
        # Negative generalized effort moves both pads toward their planes.
        command = np.clip(-effort, -control_limit_n, control_limit_n)
        control_limit_violations += int(np.any(np.abs(-effort) > control_limit_n))
        data.ctrl[:] = command
        mujoco.mj_step(model, data)

        floor_center_z = float(data.geom_xpos[floor_pad_id][2])
        wall_center_x = float(data.geom_xpos[wall_pad_id][0])
        floor_forces.append(floor_force)
        wall_forces.append(wall_force)
        floor_penetrations.append(max(0.0, pad_radius - floor_center_z))
        wall_penetrations.append(max(0.0, pad_radius - wall_center_x))
        controls.append(float(np.max(np.abs(command))))
        force_limit_violations += int(floor_force + wall_force > force_limit_n)

    floor = np.asarray(floor_forces, dtype=np.float64)
    wall = np.asarray(wall_forces, dtype=np.float64)
    tail_start = max(0, int(steps * 0.8))
    floor_tail = floor[tail_start:]
    wall_tail = wall[tail_start:]
    return DualContactMetrics(
        target_floor_force_n=target_floor_force_n,
        target_wall_force_n=target_wall_force_n,
        mean_floor_force_n=float(floor_tail.mean()),
        mean_wall_force_n=float(wall_tail.mean()),
        floor_force_rmse_n=float(np.sqrt(np.mean((floor_tail - target_floor_force_n) ** 2))),
        wall_force_rmse_n=float(np.sqrt(np.mean((wall_tail - target_wall_force_n) ** 2))),
        max_floor_penetration_m=float(max(floor_penetrations)),
        max_wall_penetration_m=float(max(wall_penetrations)),
        peak_total_force_n=float(np.max(floor + wall)),
        max_control_n=float(max(controls)),
        control_limit_violations=control_limit_violations,
        force_limit_violations=force_limit_violations,
        floor_contact_loss_rate=float(np.mean(floor <= 1e-6)),
        wall_contact_loss_rate=float(np.mean(wall <= 1e-6)),
        contacts_seen=bool(np.any(floor > 0) and np.any(wall > 0)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--target-floor", type=float, default=5.0)
    parser.add_argument("--target-wall", type=float, default=4.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(run(
        steps=args.steps,
        target_floor_force_n=args.target_floor,
        target_wall_force_n=args.target_wall,
        seed=args.seed,
    ).__dict__, indent=2))


if __name__ == "__main__":
    main()
