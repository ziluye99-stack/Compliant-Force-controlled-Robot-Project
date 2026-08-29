# Task: MuJoCo tangential contact contract

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/mujoco-tangential-contact`
- Project priority: Compliant interaction and simulation-to-real transfer
- Stage gate: MuJoCo simulation
- Related literature notes: `docs/literature/README.md`
- Dependencies or blockers: Platform-neutral scene; robot and sensor specifications remain unspecified

## Objective

Add a minimal tangential degree of freedom so the project can measure sticking,
sliding, friction ratio, and normal-force degradation under tangential load.

## Inputs and outputs

- Inputs: Verified normal-force MuJoCo baseline and fixed contact parameters
- Expected code/config/documentation artifacts: `src/tangential_contact.py`, `configs/tangential_contact.yaml`, experiment record, tests
- Expected experiment run IDs or figures: Local CLI metrics for 1 N and 4 N tangential commands

## Acceptance criteria

- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.tangential_contact --steps 1200 --target-tangential 1.0
./.mamba-env/bin/python -m src.tangential_contact --steps 1200 --target-tangential 4.0
```

## Completion note

- Git commit: `e7f2d79` (`Add MuJoCo tangential friction contact task`)
- Test output: `12 passed`; low-force sticking and high-force sliding CLI runs completed
- Artifact path: CLI JSON output; no generated data committed
- Known limitations: One sphere/plane scene, no robot kinematics or calibrated sensor model
- Follow-up task: Add a multi-DOF end-effector or arm model and identify contact parameters from measured data
