# Task: Held-out residual policy robustness study

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/residual-policy-heldout`
- Project priority: Simulation-to-real transfer and evidence/reproducibility
- Stage gate: Evaluation
- Related literature notes: `docs/literature/README.md`
- Dependencies or blockers: One-dimensional normal contact remains the current scene; tangential friction is intentionally not claimed

## Objective

Measure whether the residual policy trained on a target-force range transfers
to held-out target forces and dynamics settings across three fixed seeds.

## Inputs and outputs

- Inputs: `codex/residual-policy-baseline`, target-force range [3, 7] N, fixed disturbance contract
- Expected code/config/documentation artifacts: `src/heldout_study.py`, updated residual experiment and roadmap
- Expected experiment run IDs or figures: ignored JSON result under `artifacts/residual-heldout/`

## Acceptance criteria

- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.heldout_study --train-episodes 12 --train-steps 500 --eval-steps 1000
```

## Completion note

- Git commit: pending
- Test output: pending
- Artifact path: `artifacts/residual-heldout/results.json` (ignored by Git)
- Known limitations: Single one-dimensional contact scene; no friction claim or hardware commands
- Follow-up task: Add a tangential contact task and perform a scene-level held-out evaluation
