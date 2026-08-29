# Task: First MuJoCo contact-force baseline

Read `docs/PROJECT_VISION.md` immediately before starting this branch.

## Scope

- Branch: `codex/first-mujoco-contact-baseline`
- Project priority: Compliant interaction and evidence/reproducibility
- Stage gate: MuJoCo simulation
- Related literature notes: `docs/literature/notes/contact-survey-104224.md`, `docs/literature/related-work-taxonomy.md`
- Dependencies or blockers: Platform-neutral fixture only; no vendor driver, hardware command, or Slurm training

## Objective

Establish a config-driven, deterministic MuJoCo normal-contact force baseline
that can be rerun locally or on an explicitly allocated server and that stores
the resolved configuration, Git commit, Python package snapshot, seed, metrics,
and Slurm job ID when present.

## Inputs and outputs

- Inputs: `configs/contact_force.yaml`, fixed seed, platform-neutral interface contract
- Expected artifact: `src/contact_force_experiment.py`, config-driven test, experiment record, and ignored run directory
- Expected experiment run IDs or figures: ignored `artifacts/contact-force-baseline/<run-id>/` containing `config.yaml`, `manifest.json`, and `metrics.json`

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A measurable behavior or artifact exists
- [x] Baseline and comparison are defined: bounded PI baseline; robustness config is the comparison
- [x] Fixed seed/config and environment are recorded
- [x] Failure behavior and safety limits are documented; hardware commands remain disabled

## Verification

```bash
test -s docs/PROJECT_VISION.md
.mamba-env/bin/python -m src.contact_force_experiment \
  --config configs/contact_force.yaml --run-id first-baseline-smoke --steps 200 --seed 42
test -s artifacts/contact-force-baseline/first-baseline-smoke/manifest.json
test -s artifacts/contact-force-baseline/first-baseline-smoke/metrics.json
.mamba-env/bin/python -m pytest -q tests/test_contact_force_experiment.py tests/test_contact_force_baseline.py
```

## Completion note

- Git commit: `4d2487e` (`Add config-driven MuJoCo contact baseline`)
- Test output: `84 passed`; config-driven baseline and robust comparison completed with fixed seed 42
- Artifact path: `artifacts/contact-force-baseline/` (ignored by Git)
- Known limitations: Idealized one-dimensional fixture; no measured robot dynamics, sensor calibration, or hardware evidence
- Follow-up task: Compare one bounded residual policy against this baseline on held-out contact and dynamics conditions
