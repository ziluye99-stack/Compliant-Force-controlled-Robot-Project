# Research Roadmap

This roadmap is deliberately staged. A later stage cannot hide a missing
earlier gate. Each item should become a focused branch using
`docs/tasks/task-template.md` and should cite the relevant literature notes.

## Stage 0: Platform and evidence baseline

- [x] MuJoCo-first repository and reproducible environment
- [x] Laptop/server split, artifact archive, and shared-server safety policy
- [x] Project vision, literature source map, and paper-note workflow
- [x] Select the first MuJoCo task and define observation/action contracts
- [x] Select a non-learning baseline controller

## Stage 1: Contact task baseline

- [x] Author a minimal MuJoCo contact scene with deterministic reset
- [x] Implement a non-learning force baseline
- [x] Define force tracking, penetration, contact, and safety metrics
- [x] Add fixed-seed unit tests and short evaluation runs
- [x] Add a controlled sensor-noise and dynamics-mismatch evaluation
- [x] Add a controlled actuator-delay evaluation
- [x] Add a normal/tangential contact scene with a friction-regime test
- [x] Connect contact force control to a platform-neutral two-link arm model

## Stage 2: Data and learning

- [x] Select the first learning method and its reproducible baseline
- [x] Define demonstrations or interaction-data collection protocol
- [x] Specify train/validation/test splits and leakage checks
- [x] Train one transparent baseline before adding a new model component
- [ ] Run ablations over observations, dynamics randomization, and controller gains

## Stage 3: Transfer analysis

- [x] Define versioned contact-log schema and offline replay safety gate
- [x] Validate bias/noise/friction identification on a synthetic fixture
- [x] Export a MuJoCo planar-arm trace into `contact-log/v1` with provenance and replay checks
- [x] Add a dedicated MuJoCo sliding calibration excitation and parameter comparison
- [ ] Measure model mismatch and sensor noise from the selected hardware
- [ ] Calibrate the corresponding MuJoCo parameters
- [ ] Replay recorded trajectories offline before issuing commands
- [ ] Compare simulation and real metrics with identical evaluation code

## Stage 4: Supervised hardware

- [ ] Document robot, sensor, firmware, communication, limits, watchdog, and E-stop
- [ ] Test with motors disabled, then low-speed/low-gain under an operator
- [ ] Keep a rollback model and a bounded safe pose
- [ ] Record failures as first-class results, not only successful episodes

## Stage 5: Paper and release

- [ ] Freeze configs, environment lock, seeds, and evaluation scripts
- [ ] Archive checkpoints, videos, metrics, and manifests on the research drive
- [ ] Generate figures and equations from logged data
- [ ] Write limitations, reproducibility notes, and release checklist

## Current next decision

The next research decision is to identify contact and actuator parameters from
measured force/torque data, then replay those measurements through the planar
arm contract. Robot-specific implementation remains blocked until the robot and
sensor specifications are supplied.
