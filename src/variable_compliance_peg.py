"""MuJoCo peg-in-hole benchmark with fixed and phase-varying compliance.

The benchmark is deliberately platform neutral. It compares a fixed-gain
Cartesian controller with a bounded, phase-varying gain schedule while a
two-slide peg approaches a square hole. It never sends a hardware command.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

import mujoco
import numpy as np


MODEL_XML = """
<mujoco model="variable-compliance-peg-in-hole">
  <option timestep="0.002" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    <geom name="board_left" type="box" pos="-0.030 0 -0.040" size="0.005 0.060 0.040" friction="0.7 0.01 0.001"/>
    <geom name="board_right" type="box" pos="0.030 0 -0.040" size="0.005 0.060 0.040" friction="0.7 0.01 0.001"/>
    <geom name="board_front" type="box" pos="0 0.030 -0.040" size="0.025 0.005 0.040" friction="0.7 0.01 0.001"/>
    <geom name="board_back" type="box" pos="0 -0.030 -0.040" size="0.025 0.005 0.040" friction="0.7 0.01 0.001"/>
    <body name="peg" pos="0 0 0.100">
      <joint name="lateral_slide" type="slide" axis="1 0 0" range="-0.08 0.08" limited="true" damping="1.0"/>
      <joint name="insertion_slide" type="slide" axis="0 0 1" range="-0.10 0.02" limited="true" damping="1.5"/>
      <geom name="peg_shaft" type="cylinder" size="0.018 0.040" mass="0.25" friction="0.7 0.01 0.001"/>
      <site name="peg_tip" pos="0 0 -0.040" size="0.004" rgba="0 1 0 1"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="lateral_motor" joint="lateral_slide" gear="1"/>
    <motor name="insertion_motor" joint="insertion_slide" gear="1"/>
  </actuator>
</mujoco>
"""


@dataclass(frozen=True)
class PegInHoleMetrics:
    strategy: str
    seed: int
    success: bool
    steps: int
    peak_contact_force_n: float
    contact_active_mean_force_n: float
    tail_mean_contact_force_n: float
    max_lateral_contact_force_n: float
    final_lateral_error_m: float
    max_geometric_intrusion_m: float
    safety_gate_activations: int
    contacts_seen: bool
    outer_updates: int


def _validate_strategy(strategy: str) -> None:
    if strategy not in {"fixed", "variable"}:
        raise ValueError("strategy must be 'fixed' or 'variable'")


def _contact_forces(model: mujoco.MjModel, data: mujoco.MjData) -> tuple[float, float]:
    wrench = np.zeros(6, dtype=np.float64)
    total = 0.0
    lateral = 0.0
    for contact_id in range(data.ncon):
        mujoco.mj_contactForce(model, data, contact_id, wrench)
        total += float(np.linalg.norm(wrench[:3]))
        lateral += float(np.linalg.norm(wrench[1:3]))
    return total, lateral


def _make_system(
    *, seed: int, initial_offset_m: float, friction_coefficient: float
) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if friction_coefficient <= 0:
        raise ValueError("friction_coefficient must be positive")
    rng = np.random.default_rng(seed)
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    model.geom_friction[:, 0] = friction_coefficient
    data = mujoco.MjData(model)
    data.qpos[0] = initial_offset_m + float(rng.uniform(-0.0005, 0.0005))
    data.qpos[1] = 0.0
    mujoco.mj_forward(model, data)
    return model, data


def run(
    strategy: str = "variable",
    *,
    steps: int = 1500,
    seed: int = 42,
    initial_offset_m: float = 0.012,
    friction_coefficient: float = 0.7,
    outer_period_fast_steps: int = 25,
    target_depth_qpos_m: float = -0.080,
    search_depth_qpos_m: float = -0.035,
    force_limit_n: float = 80.0,
    intrusion_limit_m: float = 0.006,
) -> PegInHoleMetrics:
    """Run the fixed or variable-compliance insertion benchmark."""
    _validate_strategy(strategy)
    if steps < 100 or outer_period_fast_steps < 1:
        raise ValueError("steps must be at least 100 and outer period must be positive")
    if initial_offset_m < 0 or friction_coefficient <= 0:
        raise ValueError("initial offset must be non-negative and friction positive")
    if target_depth_qpos_m >= 0 or search_depth_qpos_m >= 0:
        raise ValueError("insertion depths must be negative qpos values")
    model, data = _make_system(
        seed=seed, initial_offset_m=initial_offset_m,
        friction_coefficient=friction_coefficient,
    )
    dt = model.opt.timestep
    target_x = 0.0
    integral_z = 0.0
    peak_forces: list[float] = []
    lateral_forces: list[float] = []
    intrusions: list[float] = []
    safety_activations = 0
    outer_updates = 0
    kx, dx, kz, dz = 30.0, 4.0, 260.0, 18.0
    for step in range(steps):
        contact_force, lateral_force = _contact_forces(model, data)
        if step % outer_period_fast_steps == 0:
            outer_updates += 1
            if strategy == "variable":
                # Softer lateral search above the rim, then stiff centering.
                if data.qpos[1] > search_depth_qpos_m:
                    kx, dx = 30.0, 4.0
                else:
                    kx, dx = 160.0, 10.0
            else:
                kx, dx = 30.0, 4.0
        x_error = target_x - float(data.qpos[0])
        z_error = target_depth_qpos_m - float(data.qpos[1])
        integral_z = float(np.clip(integral_z + z_error * dt, -0.08, 0.08))
        lateral_control = kx * x_error - dx * float(data.qvel[0])
        insertion_control = kz * z_error + 10.0 * integral_z - dz * float(data.qvel[1])
        control = np.clip(
            np.asarray([lateral_control, insertion_control], dtype=np.float64),
            -force_limit_n,
            force_limit_n,
        )
        geometric_intrusion = max(0.0, abs(float(data.qpos[0])) + 0.018 - 0.025)
        if contact_force > force_limit_n or geometric_intrusion > intrusion_limit_m:
            safety_activations += 1
            control[0] = 0.0
            control[1] = min(float(control[1]), 0.0)
        data.ctrl[:] = control
        mujoco.mj_step(model, data)
        geometric_intrusion = max(0.0, abs(float(data.qpos[0])) + 0.018 - 0.025)
        peak_forces.append(contact_force)
        lateral_forces.append(lateral_force)
        intrusions.append(geometric_intrusion)
    tail = slice(max(0, int(steps * 0.8)), None)
    force_values = np.asarray(peak_forces)
    active_forces = force_values[force_values > 0.0]
    final_x = abs(float(data.qpos[0]))
    success = bool(
        data.qpos[1] <= target_depth_qpos_m + 0.004
        and final_x <= 0.004
        and max(intrusions) <= intrusion_limit_m
        and max(peak_forces) <= force_limit_n
    )
    return PegInHoleMetrics(
        strategy=strategy,
        seed=seed,
        success=success,
        steps=steps,
        peak_contact_force_n=float(max(peak_forces)),
        contact_active_mean_force_n=float(active_forces.mean()) if active_forces.size else 0.0,
        tail_mean_contact_force_n=float(force_values[tail].mean()),
        max_lateral_contact_force_n=float(max(lateral_forces)),
        final_lateral_error_m=final_x,
        max_geometric_intrusion_m=float(max(intrusions)),
        safety_gate_activations=safety_activations,
        contacts_seen=bool(np.any(np.asarray(peak_forces) > 0.0)),
        outer_updates=outer_updates,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=("fixed", "variable"), default="variable")
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(asdict(run(strategy=args.strategy, steps=args.steps, seed=args.seed)), indent=2))


if __name__ == "__main__":
    main()
