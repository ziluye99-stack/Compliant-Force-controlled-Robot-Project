# Task: Two-rate residual force-control study

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/two-rate-residual-study`
- Project priority: Compliant interaction, embodied learning, and reproducibility
- Stage gate: Question and simulation design
- Related literature notes: `docs/literature/related-work-taxonomy.md`
- Dependencies or blockers: runner implementation is still pending; no hardware command path

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
- [ ] Runner implementation and CPU smoke test exist
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
```

## Completion note

- Git commit: pending
- Test output: design validation pending
- Artifact path: `artifacts/two-rate-residual/` (ignored)
- Known limitations: no runner, no statistical result, no hardware evidence
- Follow-up task: implement the two-rate runner and run the smallest falsifying test
