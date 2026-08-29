# Task: contact-loss recovery robustness matrix

Read `docs/PROJECT_VISION.md` immediately before this task.

## Scope

- Branch: `codex/contact-loss-recovery-matrix`
- Project priority: compliant interaction and evidence/reproducibility
- Stage gate: MuJoCo simulation
- Depends on: `docs/experiments/contact-loss-recovery.md`
- Blocked later stages: robot and calibrated sensor remain unspecified

## Objective

Extend the single contact-loss disturbance into a fixed-seed matrix over
sensor-noise, damping, actuator-delay, and disturbance-magnitude proxies while
retaining unsafe and non-recovery outcomes.

## Expected artifacts

- `src/contact_loss_recovery.py` mismatch-aware recovery interface
- `src/contact_loss_recovery_matrix.py` JSON matrix runner
- `configs/contact_loss_recovery_matrix.yaml`
- `docs/experiments/contact-loss-recovery-matrix.md`
- deterministic tests for nominal success, retained failure, and matrix schema

## Acceptance criteria

- [x] The project vision and simulation-only boundary are explicit
- [x] Every matrix case records its parameters, seed, metrics, and outcome
- [x] Failed cases are retained and not hidden by aggregate success counts
- [x] The nominal recovery behavior remains backward compatible
- [x] No hardware command, server-wide dependency, or scheduler change is made

## Verification

```bash
./.mamba-env/bin/python -m pytest -q tests/test_contact_loss_recovery.py tests/test_contact_loss_recovery_matrix.py
./.mamba-env/bin/python -m src.contact_loss_recovery_matrix --steps 500 --disturbance-step 200
bash scripts/preflight.sh local
```

## Known limitations

The scene is a one-dimensional synthetic contact. Noise, damping, and delay
axes are measured-parameter placeholders, not evidence about a real robot.

## Completion evidence

- Git commit: `55173bc` (`Add contact-loss recovery robustness matrix`)
- Local verification: `69 passed`; `bash scripts/preflight.sh local` passed
- Server verification: MuJoCo smoke test completed for 100 steps; config-driven
  matrix returned 36 cases, 12 safe recoveries, and 24 retained failures in
  `/tmp/codex-contact-loss-recovery-matrix.json`
- Server worktree: `/home/gbu/research/worktrees/codex-contact-loss-recovery-matrix`
