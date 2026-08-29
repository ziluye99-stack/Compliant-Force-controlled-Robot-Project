# Task: MuJoCo-first research vision and workflow

Read `docs/PROJECT_VISION.md` before starting this branch.

## Scope

- Branch: `codex/vision-workflow-mujoco`
- Project priorities: Evidence and reproducibility; simulation-to-real transfer
- Stage gate: Question, Literature, and System design
- Related artifacts: `docs/科研总览.md`, `docs/workflow.md`, `docs/literature/`, `docs/proposals/`
- Dependencies or blockers: A named robot, F/T sensor, and authorized Chinese full texts are still required before hardware claims.

## Objective

Make the project vision an explicit, reusable entry point for a MuJoCo-first
research loop covering literature discovery, authorized full-text reading,
proposal design, experiment decomposition, simulation, training, evaluation,
sim-to-real calibration, supervised hardware validation, and publication.

## Inputs and outputs

- Inputs: User research priorities, the versioned literature-source policy, and the existing platform-neutral MuJoCo scaffold.
- Expected artifacts: Chinese project overview, proposal and portal-intake templates, source policy, mechanical/sensor record template, and branch-entry checks.
- Expected experiment run IDs or figures: None; this is a workflow/documentation gate.

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read before branch work
- [x] MuJoCo is named as the primary simulator
- [x] Discovery metadata and authorized full-text evidence are separated
- [x] SCI/Nature/robotics venues and CNKI/万方 portal routes are recorded
- [x] Each stage has an evidence gate and a focused branch task format
- [x] Server, archive, and hardware safety boundaries are documented

## Verification

```bash
.mamba-env/bin/python scripts/check-branch-task.py
.mamba-env/bin/python scripts/check-literature-sources.py
git diff --check
bash scripts/preflight.sh local
.mamba-env/bin/python -m pytest -q
```

## Completion note

- Git commit:
- Test output:
- Artifact path: Documentation and templates only; large data remains on `/mnt/research-data`.
- Known limitations: Portal full texts, robot-specific calibration, and hardware commands remain unavailable until supplied and reviewed.
- Follow-up task: Select the first MuJoCo contact task and define its observation/action contract.
