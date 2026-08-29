# Task: MuJoCo planar arm contact interface

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/mujoco-planar-arm-contact`
- Project priority: Compliant interaction and transfer to larger embodiments
- Stage gate: MuJoCo simulation
- Related literature notes: `docs/literature/README.md`
- Dependencies or blockers: Platform-neutral arm; no vendor driver or hardware command

## Objective

Connect normal/tangential contact force control to a two-link arm using a
Jacobian-transpose Cartesian force interface with bounded joint torques.

## Inputs and outputs

- Inputs: Verified tangential contact contract and fixed MuJoCo geometry
- Expected code/config/documentation artifacts: `src/planar_arm_contact.py`, config, tests, and experiment record
- Expected experiment run IDs or figures: Deterministic CLI metrics for zero and 1 N tangential load

## Acceptance criteria

- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.planar_arm_contact --steps 1500 --target-tangential 0.0
./.mamba-env/bin/python -m src.planar_arm_contact --steps 1500 --target-tangential 1.0
```

## Completion note

- Git commit: `509307e` (`Add Jacobian transpose planar arm contact task`)
- Test output: `15 passed`; zero and 1 N tangential CLI runs completed
- Artifact path: CLI JSON output; no generated data committed
- Known limitations: No joint limits, actuator delay, calibration, or vendor-specific dynamics
- Follow-up task: Parameter identification from measured force/torque traces
