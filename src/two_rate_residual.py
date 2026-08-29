"""Two-rate MuJoCo residual force-control study.

The fast loop runs a bounded PI controller at the simulator timestep.  A
transparent linear policy is evaluated only every ``residual_period_fast_steps``
steps and its bounded output is held between updates.  This module is a
simulation-only experiment runner; it never sends a hardware command.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path

import mujoco
import numpy as np

from .contact_force_baseline import MODEL_XML, _normal_force


VARIANTS = ("pi_only", "trajectory_residual", "gain_residual", "joint_residual")


def _validate_variant(variant: str) -> None:
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")


def _make_system(
    damping_scale: float,
    actuator_gain: float,
    friction_scale: float,
    stiffness_scale: float = 1.0,
) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if damping_scale <= 0 or actuator_gain <= 0 or friction_scale <= 0 or stiffness_scale <= 0:
        raise ValueError("dynamics scales must be positive")
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    model.dof_damping[0] *= damping_scale
    model.actuator_gear[0, 0] *= actuator_gain
    model.geom_friction[:, 0] *= friction_scale
    # MuJoCo's contact stiffness is approximately inverse-square in solref[0].
    model.geom_solref[:, 0] /= np.sqrt(stiffness_scale)
    data = mujoco.MjData(model)
    data.qpos[0] = -0.149
    mujoco.mj_forward(model, data)
    return model, data


def _pi_control(
    target_force_n: float,
    measured_force_n: float,
    velocity: float,
    integral_error: float,
    *,
    kp: float,
    ki: float,
    kd: float,
    integral_limit: float,
    control_limit_n: float,
    dt: float,
) -> tuple[float, float, float]:
    error = target_force_n - measured_force_n
    integral_error = float(np.clip(integral_error + error * dt, -integral_limit, integral_limit))
    unclipped = -(kp * error + ki * integral_error + kd * velocity)
    return float(np.clip(unclipped, -control_limit_n, control_limit_n)), integral_error, error


def _features(target_force_n: float, measured_force_n: float, velocity: float, integral_error: float, base_control: float) -> np.ndarray:
    return np.asarray(
        [target_force_n - measured_force_n, velocity, integral_error, base_control, target_force_n],
        dtype=np.float64,
    )


def _output_dim(variant: str) -> int:
    _validate_variant(variant)
    return {"pi_only": 0, "trajectory_residual": 1, "gain_residual": 2, "joint_residual": 3}[variant]


def _output_limits(variant: str) -> np.ndarray:
    return {
        "trajectory_residual": np.asarray([10.0], dtype=np.float64),
        "gain_residual": np.asarray([0.5, 5.0], dtype=np.float64),
        "joint_residual": np.asarray([10.0, 0.5, 5.0], dtype=np.float64),
    }[variant]


@dataclass(frozen=True)
class TwoRateDataset:
    features: np.ndarray
    targets: np.ndarray
    episode_ids: np.ndarray

    def __post_init__(self) -> None:
        if self.features.ndim != 2 or self.targets.ndim != 2 or self.episode_ids.ndim != 1:
            raise ValueError("features and targets must be 2D and episode_ids must be 1D")
        if len(self.features) != len(self.targets) or len(self.features) != len(self.episode_ids):
            raise ValueError("dataset arrays must have the same number of rows")

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, features=self.features, targets=self.targets, episode_ids=self.episode_ids)


@dataclass(frozen=True)
class TwoRateLinearPolicy:
    """Ridge policy with one bounded output per residual channel."""

    weights: np.ndarray
    output_limits: np.ndarray

    @classmethod
    def fit(
        cls,
        features: np.ndarray,
        targets: np.ndarray,
        *,
        output_limits: np.ndarray,
        ridge: float = 1e-3,
    ) -> "TwoRateLinearPolicy":
        if features.ndim != 2 or targets.ndim != 2 or len(features) != len(targets):
            raise ValueError("features and targets must be matching 2D arrays")
        if len(features) == 0 or ridge < 0:
            raise ValueError("features must be non-empty and ridge must be non-negative")
        limits = np.asarray(output_limits, dtype=np.float64)
        if limits.ndim != 1 or len(limits) != targets.shape[1] or np.any(limits <= 0):
            raise ValueError("output_limits must match target columns and be positive")
        design = np.column_stack([features, np.ones(len(features))])
        regularizer = np.eye(design.shape[1], dtype=np.float64) * ridge
        regularizer[-1, -1] = 0.0
        weights = np.linalg.solve(design.T @ design + regularizer, design.T @ targets)
        return cls(weights=weights, output_limits=limits)

    def predict(self, features: np.ndarray) -> np.ndarray:
        values = np.asarray(features, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] + 1 != self.weights.shape[0]:
            raise ValueError("feature shape does not match policy")
        design = np.column_stack([values, np.ones(len(values))])
        return np.clip(design @ self.weights, -self.output_limits, self.output_limits)


def _gain_targets(command_delta: float, error: float, integral_error: float) -> np.ndarray:
    """Represent a command correction as the minimum-norm kp/ki correction."""
    denom = error * error + integral_error * integral_error + 1e-9
    return -command_delta * np.asarray([error, integral_error], dtype=np.float64) / denom


def _target_vector(variant: str, command_delta: float, error: float, integral_error: float) -> np.ndarray:
    if variant == "trajectory_residual":
        return np.asarray([command_delta], dtype=np.float64)
    gain_delta = _gain_targets(command_delta, error, integral_error)
    if variant == "gain_residual":
        return gain_delta
    if variant == "joint_residual":
        return np.asarray([0.5 * command_delta, *(-0.5 * gain_delta)], dtype=np.float64)
    raise ValueError(f"variant {variant!r} has no residual target")


def split_by_episode(dataset: TwoRateDataset, train_fraction: float = 0.8) -> tuple[TwoRateDataset, TwoRateDataset]:
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1")
    episodes = np.unique(dataset.episode_ids)
    if len(episodes) < 2:
        raise ValueError("at least two episodes are required")
    count = max(1, min(len(episodes) - 1, int(np.floor(len(episodes) * train_fraction))))
    train_ids = set(episodes[:count].tolist())
    mask = np.asarray([episode_id in train_ids for episode_id in dataset.episode_ids])
    return (
        TwoRateDataset(dataset.features[mask], dataset.targets[mask], dataset.episode_ids[mask]),
        TwoRateDataset(dataset.features[~mask], dataset.targets[~mask], dataset.episode_ids[~mask]),
    )


def collect_dataset(
    variant: str,
    *,
    episodes: int = 4,
    steps: int = 500,
    target_force_range_n: tuple[float, float] = (3.0, 7.0),
    force_noise_std_n: float = 0.2,
    damping_scale: float = 1.5,
    actuator_gain: float = 0.8,
    friction_scale: float = 1.0,
    stiffness_scale: float = 1.0,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    control_limit_n: float = 30.0,
    seed: int = 42,
) -> TwoRateDataset:
    _validate_variant(variant)
    if variant == "pi_only":
        raise ValueError("pi_only does not require a training dataset")
    if episodes < 1 or steps < 10:
        raise ValueError("episodes must be positive and steps must be at least 10")
    low, high = target_force_range_n
    if low <= 0 or high < low or force_noise_std_n < 0:
        raise ValueError("invalid target range or noise")
    rng = np.random.default_rng(seed)
    rows: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    episode_ids: list[int] = []
    for episode_id in range(episodes):
        target_force_n = float(rng.uniform(low, high))
        model, data = _make_system(damping_scale, actuator_gain, friction_scale, stiffness_scale)
        dt = model.opt.timestep
        measured_integral = 0.0
        true_integral = 0.0
        for _ in range(steps):
            true_force = _normal_force(model, data)
            measured_force = max(0.0, true_force + float(rng.normal(0.0, force_noise_std_n)))
            base_control, measured_integral, error = _pi_control(
                target_force_n, measured_force, float(data.qvel[0]), measured_integral,
                kp=kp, ki=ki, kd=kd, integral_limit=integral_limit,
                control_limit_n=control_limit_n, dt=dt,
            )
            oracle_control, true_integral, _ = _pi_control(
                target_force_n, true_force, float(data.qvel[0]), true_integral,
                kp=kp, ki=ki, kd=kd, integral_limit=integral_limit,
                control_limit_n=control_limit_n, dt=dt,
            )
            rows.append(_features(target_force_n, measured_force, float(data.qvel[0]), measured_integral, base_control))
            targets.append(_target_vector(variant, oracle_control - base_control, error, measured_integral))
            episode_ids.append(episode_id)
            data.ctrl[0] = base_control
            mujoco.mj_step(model, data)
    return TwoRateDataset(np.asarray(rows), np.asarray(targets), np.asarray(episode_ids, dtype=np.int64))


@dataclass(frozen=True)
class TwoRateMetrics:
    variant: str
    target_force_n: float
    force_rmse_n: float
    measured_force_rmse_n: float
    tail_abs_error_n: float
    max_penetration_m: float
    peak_force_n: float
    contact_loss_rate: float
    max_abs_control_n: float
    safety_gate_activations: int
    contacts_seen: bool


def _decode_action(variant: str, action: np.ndarray) -> tuple[float, float, float]:
    if variant == "trajectory_residual":
        return float(action[0]), 0.0, 0.0
    if variant == "gain_residual":
        return 0.0, float(action[0]), float(action[1])
    if variant == "joint_residual":
        return float(action[0]), float(action[1]), float(action[2])
    return 0.0, 0.0, 0.0


def run_two_rate(
    variant: str,
    policy: TwoRateLinearPolicy | None = None,
    *,
    steps: int = 200,
    target_force_n: float = 5.0,
    residual_period_fast_steps: int = 25,
    force_noise_std_n: float = 0.2,
    damping_scale: float = 1.5,
    actuator_gain: float = 0.8,
    friction_scale: float = 1.0,
    stiffness_scale: float = 1.0,
    actuator_delay_steps: int = 0,
    kp: float = 0.5,
    ki: float = 5.0,
    kd: float = 0.3,
    integral_limit: float = 10.0,
    control_limit_n: float = 30.0,
    penetration_limit_m: float = 0.001,
    seed: int = 123,
) -> TwoRateMetrics:
    _validate_variant(variant)
    if steps < 10 or target_force_n <= 0 or residual_period_fast_steps < 1:
        raise ValueError("invalid steps, target force, or residual period")
    if force_noise_std_n < 0 or actuator_delay_steps < 0:
        raise ValueError("noise and delay must be non-negative")
    if variant == "pi_only" and policy is not None:
        raise ValueError("pi_only cannot use a residual policy")
    if variant != "pi_only":
        if policy is None or policy.output_limits.shape[0] != _output_dim(variant):
            raise ValueError("policy output dimension does not match variant")
    rng = np.random.default_rng(seed)
    model, data = _make_system(damping_scale, actuator_gain, friction_scale, stiffness_scale)
    dt = model.opt.timestep
    integral_error = 0.0
    delay_queue: deque[float] = deque([0.0] * actuator_delay_steps)
    held_action = np.zeros(_output_dim(variant), dtype=np.float64)
    forces: list[float] = []
    measured_forces: list[float] = []
    controls: list[float] = []
    penetrations: list[float] = []
    gates = 0
    for step in range(steps):
        true_force = _normal_force(model, data)
        measured_force = max(0.0, true_force + float(rng.normal(0.0, force_noise_std_n)))
        base_control, integral_error, error = _pi_control(
            target_force_n, measured_force, float(data.qvel[0]), integral_error,
            kp=kp, ki=ki, kd=kd, integral_limit=integral_limit,
            control_limit_n=control_limit_n, dt=dt,
        )
        if variant != "pi_only" and step % residual_period_fast_steps == 0:
            held_action = policy.predict(_features(target_force_n, measured_force, float(data.qvel[0]), integral_error, base_control)[None, :])[0]
        command_delta, kp_delta, ki_delta = _decode_action(variant, held_action)
        adapted_control = -( (kp + kp_delta) * error + (ki + ki_delta) * integral_error + kd * float(data.qvel[0]) )
        unclipped = adapted_control + command_delta
        if not np.isfinite(unclipped):
            gates += 1
            unclipped = 0.0
        if abs(unclipped) > control_limit_n:
            gates += 1
        command = float(np.clip(unclipped, -control_limit_n, control_limit_n))
        delay_queue.append(command)
        applied = delay_queue.popleft()
        if abs(applied) > control_limit_n or not np.isfinite(applied):
            gates += 1
            applied = float(np.clip(np.nan_to_num(applied), -control_limit_n, control_limit_n))
        data.ctrl[0] = applied
        mujoco.mj_step(model, data)
        forces.append(true_force)
        measured_forces.append(measured_force)
        controls.append(applied)
        penetrations.append(max(0.0, float(-(data.qpos[0] + 0.15))))
        if penetrations[-1] > penetration_limit_m:
            gates += 1
    tail_start = max(0, int(steps * 0.8))
    force_array = np.asarray(forces, dtype=np.float64)
    measured_array = np.asarray(measured_forces, dtype=np.float64)
    tail = force_array[tail_start:]
    tail_measured = measured_array[tail_start:]
    return TwoRateMetrics(
        variant=variant,
        target_force_n=target_force_n,
        force_rmse_n=float(np.sqrt(np.mean((tail - target_force_n) ** 2))),
        measured_force_rmse_n=float(np.sqrt(np.mean((tail_measured - target_force_n) ** 2))),
        tail_abs_error_n=float(np.mean(np.abs(tail - target_force_n))),
        max_penetration_m=float(max(penetrations)),
        peak_force_n=float(max(force_array)),
        contact_loss_rate=float(np.mean(force_array <= 0.0)),
        max_abs_control_n=float(max(abs(value) for value in controls)),
        safety_gate_activations=gates,
        contacts_seen=bool(np.any(force_array > 0.0)),
    )


def train_and_evaluate(
    variant: str,
    *,
    episodes: int,
    steps: int,
    eval_steps: int,
    residual_period_fast_steps: int,
    seed: int,
    target_force_range_n: tuple[float, float] = (3.0, 7.0),
    train_damping_scale: float = 1.5,
    train_actuator_gain: float = 0.8,
    train_friction_scale: float = 1.0,
    train_stiffness_scale: float = 1.0,
    eval_target_force_n: float = 5.0,
    eval_force_noise_std_n: float = 0.2,
    eval_damping_scale: float = 1.5,
    eval_actuator_gain: float = 0.8,
    eval_friction_scale: float = 1.0,
    eval_stiffness_scale: float = 1.0,
    eval_actuator_delay_steps: int = 0,
) -> dict[str, object]:
    baseline = run_two_rate(
        "pi_only", steps=eval_steps, target_force_n=eval_target_force_n,
        force_noise_std_n=eval_force_noise_std_n, damping_scale=eval_damping_scale,
        actuator_gain=eval_actuator_gain, friction_scale=eval_friction_scale,
        stiffness_scale=eval_stiffness_scale, actuator_delay_steps=eval_actuator_delay_steps,
        residual_period_fast_steps=residual_period_fast_steps, seed=seed,
    )
    result: dict[str, object] = {"baseline": asdict(baseline)}
    if variant != "pi_only":
        dataset = collect_dataset(
            variant, episodes=episodes, steps=steps, target_force_range_n=target_force_range_n,
            damping_scale=train_damping_scale, actuator_gain=train_actuator_gain,
            friction_scale=train_friction_scale, stiffness_scale=train_stiffness_scale,
            seed=seed,
        )
        train, test = split_by_episode(dataset)
        policy = TwoRateLinearPolicy.fit(train.features, train.targets, output_limits=_output_limits(variant))
        prediction_rmse = float(np.sqrt(np.mean((policy.predict(test.features) - test.targets) ** 2)))
        residual = run_two_rate(
            variant, policy, steps=eval_steps, target_force_n=eval_target_force_n,
            residual_period_fast_steps=residual_period_fast_steps,
            force_noise_std_n=eval_force_noise_std_n, damping_scale=eval_damping_scale,
            actuator_gain=eval_actuator_gain, friction_scale=eval_friction_scale,
            stiffness_scale=eval_stiffness_scale, actuator_delay_steps=eval_actuator_delay_steps,
            seed=seed,
        )
        result.update({
            "dataset_rows": len(dataset.features),
            "train_rows": len(train.features),
            "test_rows": len(test.features),
            "test_target_rmse": prediction_rmse,
            "residual": asdict(residual),
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, default="joint_residual")
    parser.add_argument("--episodes", type=int, default=4)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--eval-steps", type=int, default=200)
    parser.add_argument("--residual-period-fast-steps", type=int, default=25)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = train_and_evaluate(
        args.variant,
        episodes=args.episodes,
        steps=args.steps,
        eval_steps=args.eval_steps,
        residual_period_fast_steps=args.residual_period_fast_steps,
        seed=args.seed,
    )
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
