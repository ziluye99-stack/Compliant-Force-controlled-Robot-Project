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

## Result

The baseline passes the local deterministic test (`4 passed`). With the fixed
seed and 2000 steps, the tail mean force is `4.99997 N`, force RMSE is
`0.000033 N`, and the maximum penetration proxy is `0.000612 m`. This is a
controller and contact-interface sanity check, not evidence of sim-to-real
transfer. It omits friction, sensor noise, actuator delay, robot kinematics,
and hardware limits.

## Next experiment

Add measured sensor noise and a controlled dynamics mismatch, then compare the
PI baseline against one learning-based residual while retaining the same force
metrics and safety bounds.
