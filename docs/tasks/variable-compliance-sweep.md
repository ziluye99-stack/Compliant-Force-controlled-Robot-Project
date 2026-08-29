# Task: Variable-compliance peg-in-hole robustness sweep

Read `docs/PROJECT_VISION.md` before filling this task.

## Scope

- Branch: `codex/variable-compliance-sweep`
- Project priority: Compliant interaction; evidence and reproducibility
- Stage gate: Evaluation
- Expected artifact: 90-case MuJoCo matrix with per-case metrics and failure retention
- Related records: `docs/experiments/variable-compliance-peg-in-hole.md`,
  `configs/variable_compliance_peg_sweep.yaml`
- Dependencies or blockers: None for simulation; hardware calibration remains out of scope

## Objective

Determine whether the phase-varying compliance schedule retains its peak-force
and safety behavior across held-out initial offsets and friction coefficients,
relative to the fixed-compliance baseline. The sweep must expose counterexamples
instead of selecting only favorable seeds.

## Inputs and outputs

- Inputs: the shared platform-neutral MuJoCo fixture and the committed YAML
  sweep configuration
- Expected code/configuration/documentation artifacts: one matrix manifest,
  incremental `results.json`, and a short aggregate result record
- Expected experiment run ID: `variable-peg-sweep-20260830`

## Acceptance criteria

- [ ] `docs/PROJECT_VISION.md` was read immediately before branch work
- [ ] Both strategies run for every seed, offset, and friction combination
- [ ] Each case retains success, force, intrusion, contact, and safety metrics
- [x] Failed cases remain in `results.json` and are included in the aggregate;
      execution errors and completed-but-unsuccessful outcomes are counted
      separately in the manifest
- [ ] Any performance claim reports per-condition results and does not claim
      sim-to-real transfer

## Verification

```bash
test -s docs/PROJECT_VISION.md
./.mamba-env/bin/python -m src.variable_compliance_matrix \
  --config configs/variable_compliance_peg_sweep.yaml \
  --run-id variable-peg-sweep-20260830
./.mamba-env/bin/python -m pytest -q
```

## Completion note

- Git commit:
- Test output:
- Artifact path:
- Known limitations: synthetic contact geometry and dynamics; no calibrated
  hardware or real-robot safety evidence
- Follow-up task: compare the sweep with measured contact logs after platform
  and sensor selection
