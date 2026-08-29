# MuJoCo Tangential Contact and Friction

## Task statement

- Branch: `codex/mujoco-tangential-contact`
- Project priority: compliant interaction and simulation-to-real transfer
- Stage gate: MuJoCo simulation
- Question: Does the contact model expose the expected transition from
  sticking to sliding when tangential force crosses the Coulomb limit?
- Hypothesis: With 5 N normal force and coefficient of friction 0.5, a 1 N
  tangential command remains in the sticking regime while a 4 N command
  saturates tangential contact force near 2.5 N and produces slip.

## Contract

- Scene: 1 kg sphere with independent normal and tangential slide joints on a
  horizontal plane; zero gravity; timestep 0.002 s.
- Observation: normal contact force, tangential contact-force magnitude, normal
  and tangential velocity.
- Action: bounded normal PI force plus bounded positive tangential force.
- Metrics: normal-force error, tangential-force RMSE, friction ratio, slip speed,
  penetration, and contact presence.

## Reproduction

```bash
./.mamba-env/bin/python -m src.tangential_contact --steps 2000 --target-tangential 1.0
./.mamba-env/bin/python -m src.tangential_contact --steps 2000 --target-tangential 4.0
```

The low-force run tests sticking; the high-force run tests sliding. This scene
is deliberately minimal and does not yet represent a robot arm's kinematics,
surface geometry, or sensor calibration.

## Result

At 5 N normal force and friction coefficient 0.5, the low-force (1 N) run
measured 4.997 N normal force, 0.999 N tangential force, friction ratio 0.200,
and maximum tangential speed 0.00132 m/s. It is classified as sticking using a
0.01 m/s slip threshold; the small residual speed is numerical solver drift.

The high-force (4 N) run reached a friction ratio of 0.500 and 1.50 m/s peak
tangential speed, so it is classified as sliding. Its mean tangential contact
force was 2.252 N, close to the 2.5 N Coulomb limit; normal-force regulation
degraded to 4.503 N under this deliberately aggressive command. This exposes a
real controller interaction to handle in a later multi-DOF study.
