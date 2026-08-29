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


SLIDING_CALIBRATION_XML = """
<mujoco model="sliding-sphere-calibration">
  <option timestep="0.002" gravity="0 0 0"/>
  <worldbody>
    <geom name="calibration_plane" type="plane" size="5 5 0.01" friction="0.5 0.01 0.001"/>
    <body name="calibration_sphere" pos="0 0 0.06">
      <freejoint/>
      <geom name="calibration_contact" type="sphere" size="0.05" mass="1" friction="0.5 0.01 0.001"/>
    </body>
  </worldbody>
</mujoco>
"""


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


def run_sliding_calibration_trace(
    *,
    steps: int = 1200,
    pre_contact_steps: int = 100,
    normal_force_n: float = 5.0,
    tangential_excitation_n: float = 8.0,
    friction_coefficient: float = 0.5,
    seed: int = 42,
    episode_id: int = 0,
) -> list[ContactSample]:
    """Generate a dedicated sliding calibration trace.

    A free sphere makes the excitation independently observable: the applied
    tangential force exceeds the configured Coulomb limit, so the contact
    wrench reaches a sliding regime instead of silently estimating friction
    from sticking data.
    """
    if steps < 10 or pre_contact_steps < 0 or pre_contact_steps >= steps:
        raise ValueError("steps must be at least 10 and pre_contact_steps must be in [0, steps)")
    if normal_force_n <= 0 or tangential_excitation_n <= 0 or friction_coefficient <= 0:
        raise ValueError("normal force, tangential excitation, and friction must be positive")
    model = mujoco.MjModel.from_xml_string(SLIDING_CALIBRATION_XML)
    model.geom_friction[:, 0] = friction_coefficient
    data = mujoco.MjData(model)
    body_id = model.body("calibration_sphere").id
    dt = model.opt.timestep
    samples: list[ContactSample] = []
    for step in range(steps):
        active = step >= pre_contact_steps
        applied_normal = normal_force_n if active else 0.0
        applied_tangent = tangential_excitation_n if active else 0.0
        data.xfrc_applied[body_id, :] = [applied_tangent, 0.0, -applied_normal, 0.0, 0.0, 0.0]
        normal_force, tangential_force = _contact_forces(model, data)
        slip_speed = abs(float(data.qvel[0])) if active else 0.0
        samples.append(ContactSample(
            timestamp_s=float(data.time),
            episode_id=episode_id,
            qpos_0_rad=float(data.qpos[0]),
            qpos_1_rad=float(data.qpos[2]),
            qvel_0_rad_s=float(data.qvel[0]),
            qvel_1_rad_s=float(data.qvel[2]),
            commanded_normal_force_n=float(applied_normal),
            commanded_tangential_force_n=float(applied_tangent),
            measured_normal_force_n=float(normal_force),
            measured_tangential_force_n=float(tangential_force),
            slip_speed_m_s=slip_speed,
            contact=bool(normal_force > 1e-6),
        ))
        mujoco.mj_step(model, data)
    return samples


def export_sliding_calibration_trace(
    path: Path,
    *,
    steps: int = 1200,
    pre_contact_steps: int = 100,
    normal_force_n: float = 5.0,
    tangential_excitation_n: float = 8.0,
    friction_coefficient: float = 0.5,
    seed: int = 42,
    episode_id: int = 0,
) -> dict[str, object]:
    samples = run_sliding_calibration_trace(
        steps=steps,
        pre_contact_steps=pre_contact_steps,
        normal_force_n=normal_force_n,
        tangential_excitation_n=tangential_excitation_n,
        friction_coefficient=friction_coefficient,
        seed=seed,
        episode_id=episode_id,
    )
    metadata = {
        "source": "mujoco",
        "model": "sliding-sphere-calibration",
        "git_commit": _git_revision(),
        "seed": seed,
        "units": {"force": "N", "position": "m", "velocity": "m/s"},
        "state_contract": "qpos_0/qvel_0 are x; qpos_1/qvel_1 are z for this calibration model",
        "friction_coefficient_configured": friction_coefficient,
        "normal_force_configured_n": normal_force_n,
        "tangential_excitation_configured_n": tangential_excitation_n,
    }
    write_contact_log(path, samples, metadata)
    identification = identify_parameters(samples, slip_threshold_m_s=0.01)
    replay = replay_safety_check(samples)
    comparison = compare_identification_to_config(
        identification,
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
    parser.add_argument("--sliding-excitation", type=float, default=8.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sliding-calibration", action="store_true")
    args = parser.parse_args()
    if args.sliding_calibration:
        report = export_sliding_calibration_trace(
            args.out,
            steps=args.steps,
            pre_contact_steps=args.pre_contact_steps,
            normal_force_n=args.target_normal,
            tangential_excitation_n=args.sliding_excitation,
            friction_coefficient=args.friction,
            seed=args.seed,
        )
    else:
        report = export_trace(
            args.out,
            steps=args.steps,
            pre_contact_steps=args.pre_contact_steps,
            target_normal_force_n=args.target_normal,
            target_tangential_force_n=args.target_tangential,
            friction_coefficient=args.friction,
            sensor_bias_n=args.sensor_bias,
            sensor_noise_std_n=args.sensor_noise_std,
            seed=args.seed,
        )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
