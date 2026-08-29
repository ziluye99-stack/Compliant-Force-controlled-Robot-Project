# Task: MuJoCo residual force policy baseline

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/residual-policy-baseline`
- Project priority: Embodied learning and evidence/reproducibility
- Stage gate: Training
- Related literature notes: `docs/literature/README.md`
- Dependencies or blockers: Uses the verified `codex/mujoco-actuator-delay` baseline; robot specifications are not required for this simulation-only task

## Objective

Test whether a bounded linear residual can correct a noisy-force PI command in
MuJoCo while preserving the baseline contact safety limits.

## Inputs and outputs

- Inputs: `configs/contact_force_robust.yaml`, MuJoCo force baseline, fixed seeds
- Expected code/config/documentation artifacts: `src/residual_policy.py`, `configs/residual_policy.yaml`, `docs/experiments/residual-policy.md`
- Expected experiment run IDs or figures: Local dataset/policy files under ignored `artifacts/residual-baseline/`

## Acceptance criteria

- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.residual_policy --episodes 8 --steps 500 --eval-steps 1000
```

## Completion note

- Git commit: `ea2b911` (`Add transparent MuJoCo residual policy baseline`)
- Test output: `8 passed`; CLI training/evaluation completed with fixed seed 123
- Artifact path: `artifacts/residual-baseline/` (ignored by Git)
- Known limitations: Single contact scene and one evaluation seed; no hardware commands
- Follow-up task: Held-out target-force/contact/friction study with at least three seeds
