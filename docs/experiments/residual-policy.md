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
- Disturbance: 0.2 N measurement noise, 1.5x damping, and 0.8x actuator gain.

## Reproduction

```bash
./.mamba-env/bin/python -m src.residual_policy \
  --episodes 8 --steps 500 \
  --dataset artifacts/residual-baseline/dataset.npz \
  --policy artifacts/residual-baseline/policy.npz
```

The command also evaluates PI and PI-plus-residual under the same disturbance
contract. Compare force RMSE, measured force RMSE, penetration, action limit,
contact presence, and per-seed results against `src.contact_force_baseline.run`.

## Short result

With 8 training episodes, 500 steps per episode, and evaluation seed 123:

| Controller | True force RMSE | Measured force RMSE | Max penetration |
| --- | ---: | ---: | ---: |
| PI baseline | 0.07917 N | 0.19776 N | 0.458 mm |
| PI + residual | 0.07091 N | 0.19581 N | 0.437 mm |

Both controllers remained in contact and below the 30 N action limit. This is
one deterministic engineering run, not a generalization or sim-to-real claim.

## Held-out study

`src/heldout_study.py` trains on target forces sampled from 3--7 N, then tests
target forces 4 and 6 N under two unseen damping/actuator settings and seeds
101, 202, and 303 (12 evaluations total). Aggregate results from the fixed
study command are:

| Controller | Mean true-force RMSE | Mean measured-force RMSE | Worst penetration |
| --- | ---: | ---: | ---: |
| PI baseline | 0.08640 N | 0.22204 N | 0.546 mm |
| PI + residual | 0.07674 N | 0.21861 N | 0.533 mm |

The residual improved both aggregate error measures in this study and stayed
within the contact/action limits. The effect is modest and comes from an
oracle-generated target in a one-dimensional scene; it is not evidence for
real-robot transfer or statistical significance.

## Limitations and next step

This is an oracle-generated supervised baseline, not a claim of improved
control or sim-to-real transfer. It uses one simple contact scene. The held-out
study varies target force and dynamics with three evaluation seeds; tangential
friction remains out of scope because the current scene has no tangential
degree of freedom. A later contact-task branch should add that degree of
freedom and a held-out scene split before any hardware consideration.
