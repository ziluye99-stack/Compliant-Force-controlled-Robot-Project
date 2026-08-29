# MuJoCo Planar Arm Contact

## Task statement

- Branch: `codex/mujoco-planar-arm-contact`
- Project priority: compliant interaction and transfer to larger embodiments
- Stage gate: MuJoCo simulation
- Question: Can a platform-neutral two-link arm regulate normal contact force
  while applying a bounded tangential force through Jacobian-transpose control?
- Hypothesis: The arm-level force interface will preserve contact and bounded
  penetration while exposing the coupling between tangential load and normal
  force regulation.

## Contract

- Scene: two revolute joints in the x-z plane, a spherical TCP, and a frictional
  horizontal plane; zero gravity; timestep 0.002 s.
- Observation: TCP position, joint velocities, normal contact force, and
  tangential contact-force magnitude.
- Action: joint torques computed from `J_p^T F_des`, bounded at 20 Nm.
- Cartesian force: positive x tangential command and negative z normal effort;
  normal effort uses bounded PI plus velocity damping.
- Metrics: normal force, tangential force, TCP position drift, torque, penetration,
  and contact presence.

## Reproduction

```bash
./.mamba-env/bin/python -m src.planar_arm_contact --steps 1500 --target-tangential 0.0
./.mamba-env/bin/python -m src.planar_arm_contact --steps 1500 --target-tangential 1.0
```

This is a kinematic/dynamic interface test, not a model of a particular vendor
arm. Joint limits, actuator bandwidth, force-sensor calibration, and safety
watchdogs remain explicit hardware inputs.

## Result

With 5 N normal force and friction coefficient 0.5, the zero-tangential-load
run reached 4.999 N mean normal force, 0.819 mm maximum penetration, and 1.38
Nm maximum joint torque. Under a 1 N tangential command it reached 4.937 N mean
normal force, 0.753 N mean tangential contact force, 0.691 mm maximum
penetration, and 1.14 Nm maximum joint torque. The normal-force drop under
tangential load is measurable coupling, not a tuning artifact to hide; later
work should add force decoupling or impedance shaping.
