# MuJoCo Residual Force Policy

## Task statement

- Branch: `codex/residual-policy-baseline`
- Project priority: embodied learning and evidence/reproducibility
- Stage gate: training
- Question: Can a transparent residual policy reduce noisy-force correction
  error while preserving the PI controller's contact safety bounds?
- Hypothesis: A linear residual trained from a true-force oracle can correct a
  noisy-force PI command without exceeding the 1 mm penetration and 30 N action
  limits in the controlled MuJoCo task.

## Contract

- Base controller: the existing bounded PI plus velocity damping controller.
- Policy input: `[target - measured_force, normal_velocity, integral_error,
  base_control, target_force]`.
- Policy output: a clipped additive force correction in newtons.
- Training target: oracle-PI command minus noisy-measurement PI command.
- Model: ridge regression with an unregularized intercept; no neural network or
  hardware command path.
- Dataset: rows are labelled with episode IDs; train/test splits are by whole
  episode to prevent adjacent-timestep leakage.
- Disturbance: 0.2 N measurement noise, 1.5x damping, 0.8x actuator gain, and
  10 simulator-step command delay. Training additionally samples damping and
  actuator gain from the ranges in `configs/residual_policy.yaml`.

## Reproduction

```bash
./.mamba-env/bin/python -m src.residual_policy \
  --config configs/residual_policy.yaml \
  --run-id residual-baseline-$(date -u +%Y%m%dT%H%M%SZ)
```

The command also evaluates PI and PI-plus-residual under the same disturbance
contract. Compare force RMSE, measured force RMSE, penetration, action limit,
contact presence, and per-seed results against `src.contact_force_baseline.run`.

## Short result

With the YAML configuration, 8 training episodes, 500 steps per episode, and
evaluation seed 123:

| Controller | True force RMSE | Measured force RMSE | Max penetration |
| --- | ---: | ---: | ---: |
| PI baseline | 0.08557 N | 0.21884 N | 0.480 mm |
| PI + residual | 0.08084 N | 0.21653 N | 0.478 mm |

Both controllers remained in contact and below the 30 N action limit. This is
one deterministic engineering run, not a generalization or sim-to-real claim.

## Held-out study

`src/heldout_study.py` trains on target forces sampled from 3--7 N, then tests
target forces 4 and 6 N under two unseen damping/actuator settings and seeds
101, 202, and 303 (12 evaluations total). Aggregate results from the fixed
configuration-driven study are:

| Controller | Mean true-force RMSE | Mean measured-force RMSE | Worst penetration |
| --- | ---: | ---: | ---: |
| PI baseline | 0.08499 N | 0.22181 N | 0.573 mm |
| PI + residual | 0.08045 N | 0.22012 N | 0.570 mm |

The residual improved both aggregate error measures in this study and stayed
within the contact/action limits. The effect is modest and comes from an
oracle-generated target in a one-dimensional scene; it is not evidence for
real-robot transfer or statistical significance.

## Reproducibility artifacts

The complete configuration-driven runs used for these tables were
`artifacts/residual-baseline/config-baseline-20260830/` and
`artifacts/residual-baseline/config-heldout-20260830/` (ignored by Git).
Each directory contains the resolved YAML, provenance manifest, and metrics;
the baseline run also contains the dataset and fitted policy.

## Limitations and next step

This is an oracle-generated supervised baseline, not a claim of improved
control or sim-to-real transfer. It uses one simple contact scene. The held-out
study varies target force and dynamics with three evaluation seeds; tangential
friction remains out of scope because the current scene has no tangential
degree of freedom. A later contact-task branch should add that degree of
freedom and a held-out scene split before any hardware consideration.
The same resolved configuration drives data collection, training, and the
held-out matrix. Each run stores `config.yaml`, `manifest.json`,
`dataset.npz`, `policy.npz`, and `metrics.json` under the configured artifact
root. Use `--episodes`, `--steps`, and `--eval-steps` only for short smoke
overrides; the YAML remains the source of truth for the experiment contract.
