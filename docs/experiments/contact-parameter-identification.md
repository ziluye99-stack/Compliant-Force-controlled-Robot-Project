# Contact Parameter Identification and Replay Contract

## Task statement

- Branch: `codex/contact-parameter-identification`
- Project priority: simulation-to-real transfer and reproducibility
- Stage gate: transfer analysis
- Question: Can a versioned force/torque log provide enough evidence to
  estimate sensor bias/noise and a friction coefficient before simulation
  replay or hardware commands?
- Hypothesis: A log with no-contact, sticking, and sliding phases can recover
  the synthetic calibration parameters within predeclared tolerances.

## Data contract

`src/contact_data.py` writes `contact-log/v1` CSV files plus a metadata sidecar.
`src/mujoco_contact_trace.py` adapts the planar-arm MuJoCo run to this schema
and emits identification, replay, and configured-parameter comparison reports.
The schema records time, episode, two joint positions/velocities, commanded and
measured normal/tangential forces, slip speed, and a contact flag. Metadata must
include the Git revision, environment identifier, sensor calibration revision,
units, and source (synthetic, MuJoCo, or hardware).

Raw logs belong on the server or `/mnt/research-data`, never in Git. A log must
pass `replay_safety_check` before it is replayed or used to generate a command.

## Offline identification

- No-contact rows estimate normal sensor bias and noise.
- Sliding rows estimate `median(|F_t| / F_n)` and report the 10--90% interval.
- At least five sliding rows and one no-contact phase are required for a valid
  result.
- The result is a calibration input, not a claim that the simulator matches a
  real arm.

## Reproduction

```bash
./.mamba-env/bin/python -m src.contact_data
tmp_dir=$(mktemp -d)
./.mamba-env/bin/python -m src.mujoco_contact_trace \
  --out "$tmp_dir/planar-arm.csv" --steps 1000 --pre-contact-steps 100 \
  --sensor-bias 0.12 --sensor-noise-std 0.01
./.mamba-env/bin/python -m src.mujoco_contact_trace --sliding-calibration --out "$tmp_dir/sliding.csv" --steps 1200 --pre-contact-steps 100 --target-normal 5.0 --sliding-excitation 8.0 --friction 0.5
./.mamba-env/bin/python -m pytest -q
```

The `contact_data` CLI uses a deterministic synthetic fixture with known friction 0.45,
normal bias 0.12 N, and 0.02 N noise. Replace the fixture with a real or MuJoCo
log only after recording its provenance and calibration metadata.

The MuJoCo adapter intentionally reports a failed friction comparison when the
trace contains sticking rather than sliding contact. A dedicated sliding
calibration excitation is available through `--sliding-calibration`; the
verified fixture recovers friction 0.457 for a configured value of 0.5. The
planar-arm trace remains the interface for future robot-specific logs.
