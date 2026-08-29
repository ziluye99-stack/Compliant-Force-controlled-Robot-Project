# Task: Dual-contact MuJoCo force-control fixture

Read `docs/PROJECT_VISION.md` immediately before branch work. This task is a
platform-neutral simulation contract and does not authorize hardware commands.

## Scope

- Branch: `codex/dual-contact-mujoco`
- Project priorities: Compliant interaction; evidence and reproducibility
- Stage gate: MuJoCo simulation and system-interface validation
- Related literature notes: `docs/literature/notes/multi-contact-whole-body-force-control-2024.md`
- Dependencies or blockers: Robot embodiment, force sensor, and hardware safety
  procedure are intentionally unspecified

## Objective

Test whether simultaneous floor and wall contact forces can be regulated
independently with bounded effort and bounded penetration in a deterministic
MuJoCo fixture.

## Inputs and outputs

- Inputs: Platform-neutral two-contact geometry, fixed seed, and interface YAML
- Expected artifacts: `src/dual_contact.py`, `configs/dual_contact.yaml`,
  interface contract, experiment record, and focused tests
- Expected result: JSON metrics from a short deterministic CLI run; generated
  artifacts remain under ignored `artifacts/`

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` is referenced as the branch-entry gate
- [x] A measurable two-contact behavior and baseline controller exist
- [x] Force, penetration, contact-loss, effort, and command-limit metrics exist
- [x] Fixed seed/config and platform-neutral safety bounds are recorded
- [x] No hardware command path is enabled

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python -m pytest -q tests/test_dual_contact.py tests/test_interface_contract.py
./.mamba-env/bin/python -m src.dual_contact --steps 1500 --seed 42
./.mamba-env/bin/python scripts/check-interface-contract.py configs/platform_neutral_interface.yaml
```

## Completion note

- Git commit: `fdbd36a` (`Freeze platform-neutral system interface`)
- Known limitations: This is not a selected robot, humanoid, calibrated sensor,
  sim-to-real result, or hardware safety approval
- Follow-up: Select the embodiment and collect measured mechanical/sensor limits
  before calibration or supervised replay
