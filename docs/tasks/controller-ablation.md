# Task: Controller and observation ablation

Read `docs/PROJECT_VISION.md` before filling this template.

## Scope

- Branch: `codex/controller-ablation`
- Project priority: Embodied learning and evidence/reproducibility
- Stage gate: Evaluation
- Expected artifact: `src/controller_ablation.py`, config, tests, and an ignored JSON result matrix

## Verification

```bash
./.mamba-env/bin/python -m pytest -q
./.mamba-env/bin/python -m src.controller_ablation --train-episodes 6 --train-steps 250 --eval-steps 400
```

## Safety and limitations

This remains a simulation-only, bounded residual policy. It does not issue
robot commands. Results do not establish sim-to-real transfer until hardware
calibration and supervised replay gates are complete.

## Completion note

- Git commit: `9649e12` (this task branch)
- Test output: `24 passed`; CLI produced 36 rows covering 2 training-dynamics settings x 3 observation settings x 2 gain variants x 3 seeds
- Follow-up: use the selected observation/gain contract in a held-out contact task
