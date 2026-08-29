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

## Stage 0.5: Literature evidence

- [x] Define source priority across robotics venues, Nature/Science, SCI, CNKI,
  and public metadata indexes
- [x] Record a dated, deduplicated discovery session with access status
- [ ] Obtain authorized full text for the contact-manipulation survey
- [x] Obtain public full text and write a structured note for the force-learning paper
- [x] Obtain public full text and write a structured note for the humanoid whole-body force-control paper
- [ ] Write a structured note for the contact-manipulation survey covering
  translation, equations, interfaces, baselines, metrics, ablations, failure
  cases, and reproducibility
- [x] Build a related-work taxonomy and identify a falsifiable project gap

## Stage 0.6: Proposal and task decomposition

- [x] Add a reviewable proposal layer between literature and experiment records
- [x] Define a platform-neutral two-rate residual force-control proposal
- [x] Decompose literature intake, platform freeze, calibration, replay, and
  supervised hardware into dependency-aware branches
- [ ] Review the proposal after the contact survey, Chinese full texts, and
  concrete robot/sensor selection are available

## Stage 0.75: System and mechanical interface

- [ ] Select the first robot embodiment and document why it fits the gap
- [ ] Freeze link/joint/contact conventions and the observation/action contract
- [ ] Record CAD revision, mass properties, transmissions, limits, and sensor
  frame/calibration requirements
- [ ] Map each MuJoCo parameter to a measured value, identification procedure,
  or explicitly justified randomization range
- [ ] Review the safety envelope, watchdog, E-stop, and rollback plan before any
  hardware command path is added

## Stage 1: Contact task baseline

- [x] Author a minimal MuJoCo contact scene with deterministic reset
- [x] Implement a non-learning force baseline
- [x] Define force tracking, penetration, contact, and safety metrics
- [x] Add fixed-seed unit tests and short evaluation runs
- [x] Add a controlled sensor-noise and dynamics-mismatch evaluation
- [x] Add a controlled actuator-delay evaluation
- [x] Add a normal/tangential contact scene with a friction-regime test
- [x] Connect contact force control to a platform-neutral two-link arm model
- [x] Add a platform-neutral simultaneous dual-contact force-control fixture
- [x] Freeze a platform-neutral system, sensing, timing, and safety interface

## Stage 2: Data and learning

- [x] Select the first learning method and its reproducible baseline
- [x] Define demonstrations or interaction-data collection protocol
- [x] Specify train/validation/test splits and leakage checks
- [x] Train one transparent baseline before adding a new model component
- [x] Run ablations over observations, dynamics randomization, and controller gains

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
- [x] Generate a reproducible SVG figure from logged matrix metrics
- [ ] Tie equation derivations and notation to the logged interfaces
- [ ] Write limitations, reproducibility notes, and release checklist

## Current next decision

The immediate next decision is literature-backed: complete the contact-
manipulation survey note and use both notes to define one falsifiable MuJoCo
experiment. In parallel, collect the selected robot and sensor specifications
needed for later transfer.
Hardware commands remain blocked until calibration, limits, watchdog, E-stop,
operator, and replay evidence are documented.

Use [`docs/literature/portal-intake.md`](literature/portal-intake.md) to hand
authorized portal PDFs into the structured-note gate without sharing portal
credentials.
