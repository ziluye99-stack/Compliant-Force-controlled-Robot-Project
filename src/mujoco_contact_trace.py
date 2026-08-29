"""Export a MuJoCo planar-arm trace using the versioned contact-log schema."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

import mujoco
import numpy as np

from .contact_data import (
    ContactSample,
    compare_identification_to_config,
    identify_parameters,
    replay_safety_check,
    write_contact_log,
)
from .planar_arm_contact import _contact_forces, _make_system


def _git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def run_trace(
    *,
    steps: int = 2000,
    pre_contact_steps: int = 100,
    target_normal_force_n: float = 5.0,
    target_tangential_force_n: float = 1.0,
    friction_coefficient: float = 0.5,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    force_limit_n: float = 30.0,
    torque_limit_nm: float = 20.0,
    sensor_bias_n: float = 0.0,
    sensor_noise_std_n: float = 0.0,
    seed: int = 42,
    episode_id: int = 0,
) -> list[ContactSample]:
    """Run the planar arm and capture one deterministic contact episode.

    The pre-contact phase provides no-contact rows for bias estimation. Slip is
    estimated from finite differences of the TCP x position, which is robust
    across MuJoCo versions that expose different velocity convenience fields.
    """
    if steps < 10 or pre_contact_steps < 0 or pre_contact_steps >= steps:
        raise ValueError("steps must be at least 10 and pre_contact_steps must be in [0, steps)")
    if target_normal_force_n <= 0 or target_tangential_force_n < 0:
        raise ValueError("target normal force must be positive and tangential force non-negative")
    if sensor_noise_std_n < 0:
        raise ValueError("sensor_noise_std_n must be non-negative")
    model, data, tcp_id = _make_system(friction_coefficient)
    rng = np.random.default_rng(seed)
    dt = model.opt.timestep
    integral_error = 0.0
    previous_tcp_x: float | None = None
    samples: list[ContactSample] = []
    for step in range(steps):
        in_contact_phase = step >= pre_contact_steps
        phase_target_normal = target_normal_force_n if in_contact_phase else 0.0
        phase_target_tangent = target_tangential_force_n if in_contact_phase else 0.0
        normal_force_n, tangential_force_n = _contact_forces(model, data)
        measured_normal_n = normal_force_n + sensor_bias_n + float(rng.normal(0.0, sensor_noise_std_n))
        measured_tangent_n = tangential_force_n + float(rng.normal(0.0, sensor_noise_std_n))
        error = phase_target_normal - measured_normal_n
        if in_contact_phase:
            integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
            normal_effort = float(np.clip(kp * error + ki * integral_error - kd * data.qvel[0], -force_limit_n, force_limit_n))
        else:
            integral_error = 0.0
            normal_effort = 0.0
        desired_force = np.asarray([phase_target_tangent, 0.0, -normal_effort], dtype=np.float64)
        jacp = np.zeros((3, model.nv), dtype=np.float64)
        jacr = np.zeros((3, model.nv), dtype=np.float64)
        mujoco.mj_jacSite(model, data, jacp, jacr, tcp_id)
        torque = np.clip(jacp.T @ desired_force, -torque_limit_nm, torque_limit_nm)
        data.ctrl[:] = torque
        tcp_x = float(data.site_xpos[tcp_id][0])
        slip_speed = 0.0 if previous_tcp_x is None else abs(tcp_x - previous_tcp_x) / dt
        samples.append(ContactSample(
            timestamp_s=float(data.time),
            episode_id=episode_id,
            qpos_0_rad=float(data.qpos[0]),
            qpos_1_rad=float(data.qpos[1]),
            qvel_0_rad_s=float(data.qvel[0]),
            qvel_1_rad_s=float(data.qvel[1]),
            commanded_normal_force_n=float(normal_effort),
            commanded_tangential_force_n=float(phase_target_tangent),
            measured_normal_force_n=float(measured_normal_n),
            measured_tangential_force_n=float(measured_tangent_n),
            slip_speed_m_s=float(slip_speed),
            contact=bool(normal_force_n > 1e-6),
        ))
        mujoco.mj_step(model, data)
        previous_tcp_x = tcp_x
    return samples


def export_trace(
    path: Path,
    *,
    steps: int = 2000,
    pre_contact_steps: int = 100,
    target_normal_force_n: float = 5.0,
    target_tangential_force_n: float = 1.0,
    friction_coefficient: float = 0.5,
    sensor_bias_n: float = 0.0,
    sensor_noise_std_n: float = 0.0,
    seed: int = 42,
    episode_id: int = 0,
) -> dict[str, object]:
    samples = run_trace(
        steps=steps,
        pre_contact_steps=pre_contact_steps,
        target_normal_force_n=target_normal_force_n,
        target_tangential_force_n=target_tangential_force_n,
        friction_coefficient=friction_coefficient,
        sensor_bias_n=sensor_bias_n,
        sensor_noise_std_n=sensor_noise_std_n,
        seed=seed,
        episode_id=episode_id,
    )
    metadata = {
        "source": "mujoco",
        "model": "planar-arm-contact",
        "git_commit": _git_revision(),
        "seed": seed,
        "units": {"force": "N", "position": "rad/m", "velocity": "rad/s or m/s"},
        "friction_coefficient_configured": friction_coefficient,
        "sensor_bias_configured_n": sensor_bias_n,
        "sensor_noise_std_configured_n": sensor_noise_std_n,
    }
    write_contact_log(path, samples, metadata)
    identification = identify_parameters(samples, slip_threshold_m_s=0.0005)
    replay = replay_safety_check(samples)
    comparison = compare_identification_to_config(
        identification,
        configured_normal_bias_n=sensor_bias_n,
        configured_friction_coefficient=friction_coefficient,
    )
    return {
        "path": str(path),
        "sample_count": len(samples),
        "identification": asdict(identification),
        "replay": asdict(replay),
        "comparison": asdict(comparison),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--pre-contact-steps", type=int, default=100)
    parser.add_argument("--target-normal", type=float, default=5.0)
    parser.add_argument("--target-tangential", type=float, default=1.0)
    parser.add_argument("--friction", type=float, default=0.5)
    parser.add_argument("--sensor-bias", type=float, default=0.0)
    parser.add_argument("--sensor-noise-std", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(json.dumps(export_trace(
        args.out,
        steps=args.steps,
        pre_contact_steps=args.pre_contact_steps,
        target_normal_force_n=args.target_normal,
        target_tangential_force_n=args.target_tangential,
        friction_coefficient=args.friction,
        sensor_bias_n=args.sensor_bias,
        sensor_noise_std_n=args.sensor_noise_std,
        seed=args.seed,
    ), indent=2))


if __name__ == "__main__":
    main()
