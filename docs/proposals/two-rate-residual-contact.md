# Proposal: two-rate residual force control for contact tasks

## Status and scope

- Status: `draft`
- Project priorities: compliant interaction, embodied learning, simulation-to-real transfer, and reproducibility
- Stage gate advanced: literature evidence to simulation-ready experiment design
- Review date: 2026-08-29 (Asia/Shanghai)
- Related records: [`PROJECT_VISION.md`](../PROJECT_VISION.md), [`learning-force-control-2003.00628.md`](../literature/notes/learning-force-control-2003.00628.md), [`residual-learning-dmp-2008.07682.md`](../literature/notes/residual-learning-dmp-2008.07682.md), [`multi-contact-whole-body-force-control-2024.md`](../literature/notes/multi-contact-whole-body-force-control-2024.md), [`two-rate-residual-study.md`](../experiments/two-rate-residual-study.md)

## Research question and hypothesis

Can a bounded residual policy running at 20 Hz over a 500 Hz-equivalent force
loop reduce held-out contact-force error without increasing penetration, peak
force, command-limit violations, contact loss, or safety-gate activations?

The hypothesis is that a residual over a transparent PI controller can improve
robustness to friction, stiffness, sensor noise, and actuator delay while the
fast loop retains bounded force behavior. The smallest falsifying result is a
short, deterministic PI-only versus residual comparison in which action bounds,
contact logging, and safety checks are exercised.

## Evidence and gap

The verified force-learning note supports a slow learned layer over a faster
force controller and documents force-limit checks. The verified humanoid note
supports explicit multi-contact wrench feasibility and robustness analysis.
The related-work taxonomy identifies a missing controlled comparison of what a
slow residual should modify under held-out contact dynamics.

The contact-manipulation survey has a verified legal arXiv preprint and a
structured note, so it can inform taxonomy and a bounded follow-up experiment;
the publisher/portal version remains unverified and cannot be represented as
the final version. Chinese CNKI/万方 papers remain discovery-only until
downloaded through the university portal, so they cannot yet justify a design
claim.

## System and interface

- Simulator: MuJoCo, platform-neutral two-link/dual-contact fixtures
- Fast controller: bounded PI loop at 500 Hz equivalent (`dt=0.002 s`)
- Policy: residual at 20 Hz, held for 25 fast steps
- Action: bounded generalized force in SI units, clipped before and after the residual
- Hardware: commands disabled; this proposal does not select a robot, sensor, or ROS distribution
- Safety: penetration and total-force limits, finite-action checks, invalid-action hold-last-safe behavior

The interface is recorded in [`platform_neutral_interface.yaml`](../../configs/platform_neutral_interface.yaml).

## Experimental design

| Factor | Values | Control or rationale |
| --- | --- | --- |
| Baseline | PI-only | Transparent reference controller |
| Residual interface | trajectory, gain, joint | Isolate what the learner modifies |
| Dynamics | nominal/randomized training; held-out friction, stiffness, noise, delay | Test robustness beyond interpolation |
| Targets | 3--7 N training; 4 and 6 N held-out | Avoid a single-target result |
| Seeds | 101, 202, 303 | Report per-seed and aggregate variation |

Primary metric is true-force RMSE on held-out episodes. Report measured-force
error, tail error, penetration, peak contact force, contact loss, command and
torque limits, safety-gate activations, and recovery time. Use paired deltas
and a bootstrap interval. A residual is not promoted unless the predeclared
safety metrics remain within tolerance.

## Branch decomposition

| Branch | Deliverable | Depends on | Smallest verification |
| --- | --- | --- | --- |
| `codex/two-rate-residual-runner` | Reproducible MuJoCo runner and matrix | Current platform-neutral contract | `src.two_rate_matrix --dry-run` |
| `codex/contact-survey-note` | Authorized survey PDF note | School portal download | `check-paper-notes.py --require-full-text --verify-files` |
| `codex/chinese-force-control-notes` | Three CNKI/万方 notes and terminology map | School portal download | Same paper-note gate |
| `codex/robot-interface-freeze` | Robot, sensor, limits, and frame contract | Selected hardware specifications | Interface validator plus review checklist |
| `codex/mujoco-calibration` | Measured-to-MuJoCo parameter map | Robot interface and logs | Calibration report and parameter tests |
| `codex/offline-replay-gate` | Real-trace replay and identical metrics | Contact-log schema and calibration | Replay safety gate |
| `codex/supervised-hardware` | Low-gain supervised test procedure | Replay, E-stop, watchdog, operator sign-off | Motors-disabled dry run |

The branches are intentionally ordered: literature and platform selection can
proceed in parallel, but calibration depends on the selected platform, and
hardware depends on calibration and replay.

## Transfer and hardware gates

No sim-to-real claim is allowed until model mismatch and sensor noise are
measured, MuJoCo parameters are calibrated, recorded trajectories pass offline
replay, and simulation and real data use the same evaluation code. No hardware
command is allowed until joint/torque/velocity/temperature limits, watchdog,
independent E-stop, safe pose, workspace exclusion zone, operator, and rollback
model are documented.

## Decision record

- Current decision: proceed with the platform-neutral MuJoCo falsifying test and
  authorized literature intake; keep hardware stages pending.
- Evidence reviewed: two verified full-text notes and the dated discovery log.
- Next review: after the survey PDF, three Chinese full texts, and a concrete
  robot/sensor specification are available.
