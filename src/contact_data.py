"""Versioned contact-log schema, offline identification, and replay checks."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


SCHEMA_VERSION = "contact-log/v1"
FIELDS = (
    "timestamp_s",
    "episode_id",
    "qpos_0_rad",
    "qpos_1_rad",
    "qvel_0_rad_s",
    "qvel_1_rad_s",
    "commanded_normal_force_n",
    "commanded_tangential_force_n",
    "measured_normal_force_n",
    "measured_tangential_force_n",
    "slip_speed_m_s",
    "contact",
)


@dataclass(frozen=True)
class ContactSample:
    timestamp_s: float
    episode_id: int
    qpos_0_rad: float
    qpos_1_rad: float
    qvel_0_rad_s: float
    qvel_1_rad_s: float
    commanded_normal_force_n: float
    commanded_tangential_force_n: float
    measured_normal_force_n: float
    measured_tangential_force_n: float
    slip_speed_m_s: float
    contact: bool

    def as_row(self) -> dict[str, object]:
        row = asdict(self)
        row["contact"] = int(self.contact)
        return row


@dataclass(frozen=True)
class IdentificationResult:
    schema_version: str
    sample_count: int
    contact_sample_count: int
    sliding_sample_count: int
    normal_bias_n: float
    normal_noise_std_n: float
    friction_coefficient: float | None
    friction_ratio_p10: float | None
    friction_ratio_p90: float | None
    valid: bool


@dataclass(frozen=True)
class ReplayReport:
    schema_version: str
    sample_count: int
    episode_count: int
    timestamps_monotonic: bool
    max_abs_commanded_normal_force_n: float
    max_abs_commanded_tangential_force_n: float
    max_measured_force_n: float
    finite_values: bool
    within_limits: bool
    safe_to_replay: bool


@dataclass(frozen=True)
class ParameterComparison:
    """Compare identified values with parameters declared by an experiment."""

    configured_normal_bias_n: float | None
    identified_normal_bias_n: float
    normal_bias_error_n: float | None
    configured_friction_coefficient: float | None
    identified_friction_coefficient: float | None
    friction_error: float | None
    within_tolerance: bool


def write_contact_log(path: Path, samples: Iterable[ContactSample], metadata: dict[str, object] | None = None) -> None:
    """Write a CSV and a sidecar metadata file; neither belongs in Git."""
    rows = list(samples)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sample.as_row() for sample in rows)
    sidecar = path.with_suffix(path.suffix + ".metadata.json")
    payload = {"schema_version": SCHEMA_VERSION, "sample_count": len(rows), **(metadata or {})}
    sidecar.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_contact_log(path: Path) -> tuple[list[ContactSample], dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"unexpected contact-log columns; expected {FIELDS}")
        samples = [
            ContactSample(
                timestamp_s=float(row["timestamp_s"]),
                episode_id=int(row["episode_id"]),
                qpos_0_rad=float(row["qpos_0_rad"]),
                qpos_1_rad=float(row["qpos_1_rad"]),
                qvel_0_rad_s=float(row["qvel_0_rad_s"]),
                qvel_1_rad_s=float(row["qvel_1_rad_s"]),
                commanded_normal_force_n=float(row["commanded_normal_force_n"]),
                commanded_tangential_force_n=float(row["commanded_tangential_force_n"]),
                measured_normal_force_n=float(row["measured_normal_force_n"]),
                measured_tangential_force_n=float(row["measured_tangential_force_n"]),
                slip_speed_m_s=float(row["slip_speed_m_s"]),
                contact=bool(int(row["contact"])),
            )
            for row in reader
        ]
    sidecar = path.with_suffix(path.suffix + ".metadata.json")
    metadata: dict[str, object] = {}
    if sidecar.exists():
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    if metadata.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema version: {metadata.get('schema_version')}")
    return samples, metadata


def identify_parameters(samples: Iterable[ContactSample], *, slip_threshold_m_s: float = 0.01) -> IdentificationResult:
    rows = list(samples)
    if not rows:
        raise ValueError("cannot identify parameters from an empty log")
    numeric = np.asarray(
        [[sample.timestamp_s, sample.qpos_0_rad, sample.qpos_1_rad, sample.qvel_0_rad_s,
          sample.qvel_1_rad_s, sample.commanded_normal_force_n, sample.commanded_tangential_force_n,
          sample.measured_normal_force_n, sample.measured_tangential_force_n, sample.slip_speed_m_s] for sample in rows],
        dtype=np.float64,
    )
    finite_values = bool(np.isfinite(numeric).all())
    no_contact = np.asarray([not sample.contact for sample in rows], dtype=bool)
    contact = np.asarray([sample.contact for sample in rows], dtype=bool)
    sliding = np.asarray([sample.contact and sample.slip_speed_m_s >= slip_threshold_m_s for sample in rows], dtype=bool)
    no_contact_force = numeric[no_contact, 7]
    normal_bias = float(no_contact_force.mean()) if len(no_contact_force) else 0.0
    normal_noise = float(no_contact_force.std()) if len(no_contact_force) else 0.0
    normal = numeric[sliding, 7]
    tangent = np.abs(numeric[sliding, 8])
    valid_ratio = (normal > 0.1) & np.isfinite(tangent)
    ratios = tangent[valid_ratio] / normal[valid_ratio] if np.any(valid_ratio) else np.asarray([], dtype=np.float64)
    friction = float(np.median(ratios)) if len(ratios) else None
    p10 = float(np.quantile(ratios, 0.1)) if len(ratios) else None
    p90 = float(np.quantile(ratios, 0.9)) if len(ratios) else None
    valid = finite_values and bool(len(no_contact_force)) and len(ratios) >= 5
    return IdentificationResult(
        schema_version=SCHEMA_VERSION,
        sample_count=len(rows),
        contact_sample_count=int(contact.sum()),
        sliding_sample_count=int(sliding.sum()),
        normal_bias_n=normal_bias,
        normal_noise_std_n=normal_noise,
        friction_coefficient=friction,
        friction_ratio_p10=p10,
        friction_ratio_p90=p90,
        valid=valid,
    )


def replay_safety_check(
    samples: Iterable[ContactSample],
    *,
    normal_command_limit_n: float = 30.0,
    tangential_command_limit_n: float = 10.0,
    max_step_dt_s: float = 0.1,
) -> ReplayReport:
    """Check a log before replaying it in simulation or sending it to hardware."""
    rows = list(samples)
    if not rows:
        raise ValueError("cannot replay an empty log")
    finite = all(np.isfinite(list(asdict(sample).values())[:-1]).all() for sample in rows)
    monotonic = True
    for previous, current in zip(rows, rows[1:]):
        if current.episode_id == previous.episode_id:
            dt = current.timestamp_s - previous.timestamp_s
            monotonic = monotonic and 0.0 < dt <= max_step_dt_s
    max_normal = max(abs(sample.commanded_normal_force_n) for sample in rows)
    max_tangent = max(abs(sample.commanded_tangential_force_n) for sample in rows)
    max_measured = max(max(sample.measured_normal_force_n, 0.0) for sample in rows)
    within_limits = max_normal <= normal_command_limit_n and max_tangent <= tangential_command_limit_n
    safe = finite and monotonic and within_limits
    return ReplayReport(
        schema_version=SCHEMA_VERSION,
        sample_count=len(rows),
        episode_count=len({sample.episode_id for sample in rows}),
        timestamps_monotonic=monotonic,
        max_abs_commanded_normal_force_n=float(max_normal),
        max_abs_commanded_tangential_force_n=float(max_tangent),
        max_measured_force_n=float(max_measured),
        finite_values=finite,
        within_limits=within_limits,
        safe_to_replay=safe,
    )


def compare_identification_to_config(
    result: IdentificationResult,
    *,
    configured_normal_bias_n: float | None = None,
    configured_friction_coefficient: float | None = None,
    normal_bias_tolerance_n: float = 0.05,
    friction_tolerance: float = 0.1,
) -> ParameterComparison:
    """Report whether identified parameters agree with declared values.

    A missing configured value is reported as unknown rather than treated as a
    pass. This keeps calibration evidence separate from simulator metadata.
    """
    if normal_bias_tolerance_n < 0 or friction_tolerance < 0:
        raise ValueError("comparison tolerances must be non-negative")
    bias_error = (
        abs(result.normal_bias_n - configured_normal_bias_n)
        if configured_normal_bias_n is not None
        else None
    )
    friction_error = (
        abs(result.friction_coefficient - configured_friction_coefficient)
        if result.friction_coefficient is not None and configured_friction_coefficient is not None
        else None
    )
    checks: list[bool] = []
    if bias_error is not None:
        checks.append(bias_error <= normal_bias_tolerance_n)
    if friction_error is not None:
        checks.append(friction_error <= friction_tolerance)
    return ParameterComparison(
        configured_normal_bias_n=configured_normal_bias_n,
        identified_normal_bias_n=result.normal_bias_n,
        normal_bias_error_n=bias_error,
        configured_friction_coefficient=configured_friction_coefficient,
        identified_friction_coefficient=result.friction_coefficient,
        friction_error=friction_error,
        within_tolerance=bool(result.valid and checks and all(checks)),
    )


def synthetic_calibration_log(*, samples_per_phase: int = 20, friction_coefficient: float = 0.45, seed: int = 42) -> list[ContactSample]:
    """Create a deterministic calibration fixture without hardware access."""
    if samples_per_phase < 5 or friction_coefficient <= 0:
        raise ValueError("samples_per_phase must be at least 5 and friction must be positive")
    rng = np.random.default_rng(seed)
    rows: list[ContactSample] = []
    dt = 0.002
    for index in range(samples_per_phase * 3):
        phase = index // samples_per_phase
        contact = phase > 0
        sliding = phase == 2
        true_normal = 0.0 if not contact else 5.0
        measured_normal = true_normal + 0.12 + float(rng.normal(0.0, 0.02))
        measured_tangent = 0.0 if not sliding else friction_coefficient * true_normal + float(rng.normal(0.0, 0.015))
        rows.append(ContactSample(
            timestamp_s=index * dt,
            episode_id=0,
            qpos_0_rad=0.1 * index,
            qpos_1_rad=-0.2,
            qvel_0_rad_s=0.0,
            qvel_1_rad_s=0.0 if not sliding else 0.1,
            commanded_normal_force_n=5.0 if contact else 0.0,
            commanded_tangential_force_n=0.0 if not sliding else 4.0,
            measured_normal_force_n=measured_normal,
            measured_tangential_force_n=measured_tangent,
            slip_speed_m_s=0.0 if not sliding else 0.2,
            contact=contact,
        ))
    return rows


if __name__ == "__main__":
    samples = synthetic_calibration_log()
    print(json.dumps({"identification": asdict(identify_parameters(samples)), "replay": asdict(replay_safety_check(samples))}, indent=2))
