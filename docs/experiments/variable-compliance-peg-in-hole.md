# MuJoCo Variable-Compliance Peg-in-Hole

- Stage gate: MuJoCo simulation
- Question: Can phase-varying bounded lateral compliance lower contact force
  without reducing insertion success under pose error?
- Related literature: `docs/literature/notes/variable-compliance-peg-in-hole-2020.md`
- Config: `configs/variable_compliance_peg.yaml`
- Runner: `src.variable_compliance_peg`

## Design

The scene uses a platform-neutral two-slide peg, a square opening, and four
frictional board walls. The 500 Hz inner loop applies bounded Cartesian slide
forces. The 20 Hz outer update chooses either fixed high gains or a variable
schedule: soft lateral search above the rim, then a stiffer centering phase.
Both strategies share the same target depth, force limit, initial offset, and
seed.

## Metrics and controls

Report insertion success, peak contact force, contact-active mean force, tail
mean contact force, maximum lateral contact force, final lateral error,
geometric intrusion proxy, and safety-gate activations. The contact-active mean
uses only time steps with nonzero contact; the tail mean uses the final 20% of
all steps and may be zero after insertion has cleared the rim. Run seeds 101,
202, and 303. Retain failures and the exact Git commit in the run manifest.
This experiment does not establish sim-to-real or hardware performance.

## Current status

The fixed-seed smoke test succeeds for both strategies. The separate three-seed
run below is retained as an initial regression record; every trial succeeded
without a safety-gate activation.

| Seed | Fixed peak force (N) | Variable peak force (N) |
| ---: | ---: | ---: |
| 101 | 11.297 | 11.594 |
| 202 | 11.289 | 3.953 |
| 303 | 11.287 | 3.951 |

Seed 42 is a nominal smoke test where the fixed and variable values are 51.76
N and 4.05 N respectively. The seed-101 counterexample means the current
evidence does not establish a statistically reliable improvement; the next
iteration must add more seeds and pose/friction sweeps before a conclusion.
These values are synthetic MuJoCo regression evidence, not a sim-to-real claim.
Contact parameters remain synthetic until a mechanical fixture is selected and
measured.
