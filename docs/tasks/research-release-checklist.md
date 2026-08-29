# Task: Research release readiness contract

Read `docs/PROJECT_VISION.md` before working on this branch.

## Scope

- Branch: `codex/research-release-checklist`
- Project priority: Evidence and reproducibility
- Stage gate: Publication
- Expected artifact: a versioned release checklist and a structural readiness checker
- Dependencies: experiment records, literature notes, environment lock, and archived artifacts

## Objective

Make the transition from a completed MuJoCo evaluation to a paper or release
reviewable. The checker validates the repository contract; a human still marks
run-specific evidence and must not promote simulation results to hardware claims.

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] The checklist covers provenance, seeds, splits, metrics, failures, figures,
      equations, literature evidence, and hardware boundaries
- [x] The checker fails when a required release input or checklist section is missing
- [x] Local preflight invokes the checker
- [x] No credentials, raw data, checkpoints, videos, or hardware commands are added

## Verification

```bash
./.mamba-env/bin/python scripts/check-release-readiness.py
./.mamba-env/bin/python -m pytest -q tests/test_release_readiness.py
bash scripts/preflight.sh local
```

## Known limitations

This task does not assert that any particular run is publication-ready. Formal
publisher/CNKI evidence, calibrated hardware data, and supervised real-robot
validation remain separate stage gates.

## Completion note

- Git commit: `c02349c` (`Add reproducible research release checklist`)
- Test output: local preflight passed; `91 passed`
- Artifact path: checklist and checker are versioned; run artifacts remain outside Git
- Follow-up task: fill the checklist for a selected multi-seed result after literature and hardware gates
