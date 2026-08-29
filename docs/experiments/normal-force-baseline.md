# Normal Contact Force Tracking Baseline

## Task statement

- Branch: `codex/mujoco-normal-force-baseline`
- Project priority: compliant interaction and reproducibility
- Stage gate: MuJoCo simulation
- Question: Can a minimal contact-aware PI controller track a constant normal
  force on a rigid plane without excessive penetration?
- Hypothesis: With a fixed-step MuJoCo contact and bounded PI action, the steady
  force error can remain below 0.05 N in this idealized task.

## Setup

- Scene: 1 kg spherical end-effector with one normal slide joint and a rigid
  plane; zero gravity; timestep 0.002 s.
- Observation: summed positive normal contact force and normal joint velocity.
- Action: bounded motor force in the normal direction.
- Controller: PI force error plus velocity damping; integral anti-windup.
- Target: 5.0 N; 2000 steps; seed 42.
- Config: `configs/contact_force.yaml`.

## Metrics and acceptance

- Tail mean force error: `< 0.02 N` for the regression test.
- Tail force RMSE: `< 0.05 N`.
- Maximum geometric penetration proxy: `< 1 mm`.
- Determinism: same inputs produce identical metrics.

The robustness extension uses `force_noise_std_n=0.2`, `damping_scale=1.5`, and
`actuator_gain=0.8` to represent a controlled sensor and dynamics mismatch.

## Result

The baseline passes the local deterministic test (`4 passed`). With the fixed
seed and 2000 steps, the tail mean force is `4.99997 N`, force RMSE is
`0.000033 N`, and the maximum penetration proxy is `0.000612 m`. This is a
controller and contact-interface sanity check, not evidence of sim-to-real
transfer. It omits friction, sensor noise, actuator delay, robot kinematics,
and hardware limits.

With `configs/contact_force_robust.yaml`, the same controller remains stable
under 0.2 N measurement noise, 1.5x joint damping, and 0.8x actuator gain:
the true tail mean is `4.99385 N`, true-force RMSE is `0.07984 N`, and maximum
penetration is `0.000460 m`. The measured-force RMSE is `0.21810 N`, which is
reported separately because the controller cannot remove measurement noise.

## Next experiment

Add measured sensor noise and a controlled dynamics mismatch, then compare the
PI baseline against one learning-based residual while retaining the same force
metrics and safety bounds.
