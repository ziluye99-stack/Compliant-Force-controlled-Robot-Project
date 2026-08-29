# Task: MuJoCo variable-compliance peg-in-hole benchmark

Read `docs/PROJECT_VISION.md` before starting this branch.

## Scope

- Branch: `codex/variable-compliance-peg-in-hole`
- Project priority: Compliant interaction and evidence/reproducibility
- Stage gate: MuJoCo simulation
- Related paper: `docs/literature/notes/variable-compliance-peg-in-hole-2020.md`

## Question and hypothesis

Does a bounded, phase-varying lateral compliance schedule reduce contact force
while preserving insertion success under initial lateral pose error, compared
with a fixed high-gain controller? The minimum falsifiable test is a matched
MuJoCo scene, seed, force limit, and insertion target with `fixed` and
`variable` strategies.

## Expected artifact and safety boundary

- `src/variable_compliance_peg.py`
- `configs/variable_compliance_peg.yaml`
- `docs/experiments/variable-compliance-peg-in-hole.md`
- Metrics: success, peak/mean contact force, lateral force, intrusion, final
  error, and safety-gate activations.
- Simulation only. No robot driver, ROS command, or hardware actuation is
  included or authorized by this task.

## Verification

```bash
./.mamba-env/bin/python -m src.variable_compliance_peg --strategy fixed
./.mamba-env/bin/python -m src.variable_compliance_peg --strategy variable
./.mamba-env/bin/python -m pytest -q
```

## Follow-up

Run the three configured seeds, retain failed trials, and only then add sensor
noise, actuator delay, and measured contact-parameter ranges. A learned policy
must use this controller interface and safety envelope rather than bypassing it.
