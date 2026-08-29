# Variable-Compliance Peg Sweep

- Run ID: `variable-peg-sweep-20260830`
- Git commit: `b19342cd143f4eb4a30101e0ea1802ca1f68d5b1`
- Artifact: `artifacts/variable-compliance-peg-sweep/variable-peg-sweep-20260830/`
- Matrix: 2 strategies x 5 seeds x 3 offsets x 3 friction coefficients = 90 cases

## Outcome

All 90 cases executed without Python errors. Sixty cases succeeded and 30
completed with `success=false`; the latter are retained in `results.json` and
counted in the manifest as `failure_count=30`,
`unsuccessful_case_count=30`, and `execution_error_count=0`.

| Initial offset | Fixed success | Variable success | Fixed peak mean (N) | Variable peak mean (N) |
| ---: | ---: | ---: | ---: | ---: |
| 0.006 m | 15/15 | 15/15 | 0.000 | 0.000 |
| 0.012 m | 15/15 | 15/15 | 11.983 | 7.381 |
| 0.018 m | 0/15 | 0/15 | 30.399 | 30.399 |

The `0.018 m` condition activates the safety gate on every step (22,500
activations per strategy) and exceeds the synthetic intrusion limit. This is a
shared failure mode, not evidence that either controller is safer. Across all
45 paired conditions, the variable schedule reduced peak force in 10 pairs and
contact-active mean force in 9 pairs. The current simulation therefore supports
only a condition-specific force reduction around the `0.012 m` offset; it does
not establish a universally better controller or sim-to-real performance.

## Reproduction

```bash
./.mamba-env/bin/python -m src.variable_compliance_matrix \
  --config configs/variable_compliance_peg_sweep.yaml \
  --run-id variable-peg-sweep-20260830
./.mamba-env/bin/python -m pytest -q
```

Known limitations: the contact geometry, friction, dynamics, and force
thresholds are synthetic. Hardware calibration, sensor noise, watchdogs, and
real-robot safety validation remain separate stage gates.
