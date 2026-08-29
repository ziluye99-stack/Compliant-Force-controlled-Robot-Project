# Dual-contact force-control fixture

## Task statement

- Branch: `codex/dual-contact-mujoco`
- Project priorities: compliant interaction and evidence/reproducibility
- Stage gate: simulation implementation and contract validation
- Related literature: `docs/literature/notes/multi-contact-whole-body-force-control-2024.md`
- Expected artifact: deterministic MuJoCo fixture with simultaneous floor/wall force metrics

## Scope and question

This platform-neutral fixture asks whether two simultaneous contact forces can
be regulated independently while keeping penetration and total effort bounded.
It is an interface test inspired by multi-contact whole-body control; it is not
a humanoid model, a mechanical design, or evidence of sim-to-real transfer.

The tool has two slide degrees of freedom on one rigid body. One spherical pad
contacts a horizontal plane and the other contacts a vertical plane. The
controller runs at 500 Hz equivalent and maps each force error to a bounded
inward generalized effort.

## Reproduction

```bash
./.mamba-env/bin/python -m src.dual_contact --steps 1500 --seed 42
./.mamba-env/bin/python -m pytest -q tests/test_dual_contact.py
```

The source and configuration are `src/dual_contact.py` and
`configs/dual_contact.yaml`. A run record must copy the config, Git commit,
seed, dependency snapshot, and output path into `artifacts/<run-id>`; generated
artifacts remain ignored by Git.

## Metrics and boundary

The acceptance contract checks both force RMSE values, per-contact penetration,
contact-loss rates, peak total force, and command-limit violations. The result
can falsify the fixture/controller interface, but it cannot establish a claim
about a selected arm, humanoid, sensor, or real hardware. Those claims remain
blocked until the system/mechanical interface and calibration gates in the
roadmap are completed.
