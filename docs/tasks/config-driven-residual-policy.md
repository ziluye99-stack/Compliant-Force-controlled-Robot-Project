# Task: Configuration-driven residual policy loop

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/config-driven-residual-policy`
- Project priority: Embodied learning and evidence/reproducibility
- Stage gates: Training and evaluation
- Related literature notes: `docs/literature/README.md`
- Dependency: the verified MuJoCo residual-policy baseline and held-out study

## Objective

Make data collection, ridge-policy training, and held-out evaluation consume
`configs/residual_policy.yaml` so a run can be rebuilt without hidden CLI
defaults or hard-coded experiment conditions.

## Expected artifact and evidence

- A configuration-driven CLI with backward-compatible overrides
- A run directory containing the resolved config, provenance manifest, dataset,
  policy, and metrics
- Episode-level split and fixed-seed tests

## Verification

```bash
./.mamba-env/bin/python -m pytest -q tests/test_residual_policy.py tests/test_heldout_study.py
./.mamba-env/bin/python -m src.residual_policy --config configs/residual_policy.yaml --run-id smoke-config --episodes 3 --steps 30 --eval-steps 40
./.mamba-env/bin/python -m src.heldout_study --config configs/residual_policy.yaml --run-id smoke-heldout --train-episodes 4 --train-steps 30 --eval-steps 40
```

The smoke artifacts are ignored by Git and may be removed after inspection.
