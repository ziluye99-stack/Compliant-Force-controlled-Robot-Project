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

## Limitations and next step

This is an oracle-generated supervised baseline, not a claim of improved
control or sim-to-real transfer. It uses one simple contact scene and fixed
target force. The next experiment should vary target force and contact/friction
conditions, add a held-out scene split, and compare against the PI baseline
with at least three seeds before any hardware consideration.
