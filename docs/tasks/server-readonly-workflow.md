# Task: Read-only shared-server workflow

Read `docs/PROJECT_VISION.md` immediately before filling this task.

## Scope

- Branch: `codex/server-readonly-workflow`
- Project priority: Evidence and reproducibility
- Stage gate: Training
- Related documentation: `docs/workflow.md`, `docs/server-inventory.md`
- Dependencies or blockers: the shared workstation has no verified Slurm scheduler

## Objective

Provide a user-space, read-only server status command that reports GPU,
environment, disk, and scheduler state without launching a job or changing
shared system configuration.

## Expected artifact

- `scripts/server-status.sh`
- documented no-Slurm behavior and safe next action

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined: status-only checks versus job submission
- [x] Fixed command and host are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
bash -n scripts/server-status.sh
bash scripts/server-status.sh
```

## Completion note

- Git commit: pending
- Test output: pending
- Artifact path: terminal inventory only
- Known limitations: no scheduler or long-running training is enabled
- Follow-up task: obtain an approved scheduler or explicit reservation procedure
