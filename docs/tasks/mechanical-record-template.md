# Task: Mechanical and sensor platform record

Read `docs/PROJECT_VISION.md` before filling this task.

## Scope

- Branch: `codex/mechanical-record-template`
- Project priority: Simulation-to-real transfer and evidence reproducibility
- Stage gate: System design
- Related literature notes: `docs/literature/notes/` (interface and calibration evidence)
- Dependencies or blockers: A named robot is not required for the template; hardware promotion remains blocked until one is selected.

## Objective

Provide a reviewable platform record that separates measured mechanical and
sensor facts from estimates and MuJoCo randomization, so later controller or
learning results cannot be interpreted without a parameter-to-evidence map.

## Inputs and outputs

- Inputs: Platform specifications when available, the platform-neutral control interface, and safety requirements.
- Expected artifact: `docs/mechanics/platform-record-template.md` and its usage guide.
- Expected experiment run IDs or figures: None; this branch is documentation-only.

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
test -s docs/mechanics/platform-record-template.md
rg -n "MuJoCo parameter map|emergency-stop|motors-disabled replay|SHA-256" docs/mechanics/platform-record-template.md
git diff --check
```

## Completion note

- Git commit:
- Test output:
- Artifact path: None; template only
- Known limitations: No robot-specific values are asserted.
- Follow-up task: Fill a candidate-platform record after robot and F/T sensor selection.
