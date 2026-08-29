# Task: Two-rate residual force-control study

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/two-rate-residual-study`
- Project priority: Compliant interaction, embodied learning, and reproducibility
- Stage gate: Simulation implementation and contract validation
- Related literature notes: `docs/literature/related-work-taxonomy.md`
- Dependencies or blockers: complete matrix and scheduler/reservation remain pending; no hardware command path

## Objective

Define a falsifiable comparison of a bounded 20 Hz residual over a 500 Hz-equivalent
MuJoCo PI loop, including held-out dynamics and explicit safety metrics.

## Expected artifacts

- `docs/experiments/two-rate-residual-study.md`
- `configs/two_rate_residual.yaml`
- `docs/literature/related-work-taxonomy.md`
- Later implementation: runner, tests, and ignored result matrix

## Acceptance criteria

- [x] `docs/PROJECT_VISION.md` was read immediately before branch work
- [x] A falsifiable question, hypothesis, variables, baseline, and metrics exist
- [x] Observation/action and safety contracts are explicit
- [x] Fixed seeds, held-out settings, and artifact rules are defined
- [x] Runner implementation and CPU smoke test exist
- [ ] Three-seed matrix is executed and reviewed

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python - <<'PY'
from pathlib import Path
import yaml

config = yaml.safe_load(Path("configs/two_rate_residual.yaml").read_text())
assert config["control"]["fast_rate_hz"] == 500
assert config["control"]["residual_rate_hz"] == 20
assert config["training"]["split"] == "episode"
print("two-rate design config valid")
PY
./.mamba-env/bin/python -m pytest -q tests/test_two_rate_residual.py
./.mamba-env/bin/python -m src.two_rate_residual \
  --variant joint_residual \
  --episodes 2 \
  --steps 20 \
  --eval-steps 40 \
  --residual-period-fast-steps 5
```

## Completion note

- Git commit: `ce44c5b` (`Implement two-rate residual runner`)
- Test output: 29 tests passed; short `joint_residual` runner smoke completed
- Artifact path: `artifacts/two-rate-residual/` (ignored)
- Known limitations: no complete three-seed matrix, no statistical result, no hardware evidence
- Follow-up task: execute the complete held-out matrix only after a scheduler or explicit lab reservation is confirmed
