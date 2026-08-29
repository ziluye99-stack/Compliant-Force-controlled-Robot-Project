# Task: Contact parameter identification and replay contract

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/contact-parameter-identification`
- Project priority: Simulation-to-real transfer and reproducibility
- Stage gate: Transfer analysis
- Related literature notes: `docs/literature/README.md`
- Dependencies or blockers: Real logs require robot and sensor specifications; this branch uses a synthetic fixture only

## Objective

Define and validate an offline contact-log schema, sensor bias/noise estimator,
friction estimator, and replay safety gate.

## Inputs and outputs

- Inputs: Versioned contact-log CSV and metadata sidecar
- Expected code/config/documentation artifacts: `src/contact_data.py`, `src/mujoco_contact_trace.py`, config, tests, experiment record
- Expected experiment run IDs or figures: Synthetic calibration report only

## Acceptance criteria

- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.contact_data
```

## Completion note

- Git commit: `04160df` (this task branch)
- Test output: `18 passed`; synthetic identification and replay safety checks returned `valid: true` and `safe_to_replay: true`
- Artifact path: Synthetic output only; real logs remain outside Git
- Known limitations: No real sensor calibration; the current trace is mostly sticking contact and is not sufficient for friction calibration
- Follow-up task: Add a dedicated sliding excitation, then compare identified and configured friction parameters before real-log replay
