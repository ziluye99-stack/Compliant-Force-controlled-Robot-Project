# Task: contact loss and recovery evaluation

Read `docs/PROJECT_VISION.md` immediately before this task.

## Scope

- Branch: `codex/contact-loss-recovery`
- Project priority: compliant interaction and evidence/reproducibility
- Stage gate: simulation
- Related literature notes: `docs/literature/related-work-taxonomy.md`, `docs/literature/notes/contact-survey-104224.md`
- Dependencies or blockers: selected robot and calibrated sensor remain pending; this branch is simulation-only

## Objective

Measure whether the bounded MuJoCo PI force loop detects and recovers from a
repeatable contact-loss disturbance without violating force, penetration, or
command safety limits.

## Expected artifact

- `src/contact_loss_recovery.py`
- `configs/contact_loss_recovery.yaml`
- `docs/experiments/contact-loss-recovery.md`
- Fixed-seed tests and explicit loss/recovery metrics

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] The disturbance, loss threshold, recovery hold, and safety limits are explicit
- [x] Both recovery and non-recovery outcomes are represented
- [x] The experiment remains platform-neutral and simulation-only
- [x] A deterministic test and a rejection test exist

## Verification

```bash
./.mamba-env/bin/python -m pytest -q tests/test_contact_loss_recovery.py
./.mamba-env/bin/python -m src.contact_loss_recovery --steps 900 --disturbance-step 300
bash scripts/preflight.sh local
```

## Completion note

- Git commit:
- Test output:
- Artifact path: ignored `artifacts/contact-loss-recovery/`
- Known limitations: synthetic one-dimensional contact and no hardware evidence
- Follow-up task: repeat with measured contact logs after platform/interface freeze
