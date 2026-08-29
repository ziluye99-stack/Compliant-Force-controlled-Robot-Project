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

## Stage 2: Data and learning

- [ ] Select the first learning method and its reproducible baseline
- [ ] Define demonstrations or interaction-data collection protocol
- [ ] Specify train/validation/test splits and leakage checks
- [ ] Train one transparent baseline before adding a new model component
- [ ] Run ablations over observations, dynamics randomization, and controller gains

## Stage 3: Transfer analysis

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

The next research decision is the first MuJoCo contact task. It should be small
enough to run locally and representative enough to exercise force sensing or
contact stability. Robot-specific implementation remains blocked until the
robot and sensor specifications are supplied.
