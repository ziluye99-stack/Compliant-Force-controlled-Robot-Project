# Research Workflow

This repository defines the common path from an experiment idea to simulation,
training, evaluation, and supervised hardware validation. Robot-specific
drivers and control limits must be supplied before the hardware stages are
enabled.

## 0. Reconfirm the vision and evidence boundary

Before creating a branch or starting a substantial change, read
`docs/PROJECT_VISION.md` and create a focused task from
`docs/tasks/task-template.md`. The task must name one project priority, one
stage gate, the expected artifact, and the smallest verification command. Do
not start implementation from an uncited idea: the literature log and paper
notes must state what is known, what is missing, and which claim the experiment
can falsify.

## 1. Form the proposal and design the experiment

Start with `docs/proposals/template.md` when the work changes the research
direction or combines multiple experiments. The proposal must connect verified
literature to one falsifiable question, record missing evidence, and split the
work into focused branches with dependencies and smallest verification commands.
For a single experiment, continue with `docs/experiments/template.md` and state
one question, one hypothesis, the baseline, independent variables, controlled
variables, success metrics, and hardware safety constraints. Create or update a
YAML file under `configs/` and review it before running code.

Every run must have a unique `run_id`, fixed seed, committed Git revision, and
an artifact directory. Do not put raw data, checkpoints, videos, or credentials
in Git.

## 2. Freeze the system and mechanical interface

Before interpreting a controller or learned policy, write the platform-neutral
system contract and, once a platform is selected, the corresponding mechanical
record. At minimum record:

- links, joints, mass/inertia, transmission, contact geometry, and CAD revision;
- joint/torque/velocity/temperature limits and the safe operating envelope;
- force/torque sensor location, frame convention, calibration, rate, bias, and
  filtering;
- observation/action units, timing, latency budget, controller ownership, and
  failure behavior;
- which parameters are measured, identified, randomized, or intentionally held
  fixed in MuJoCo.

Keep large CAD, raw meshes, and sensor dumps on the research drive. Commit the
small metadata, exported model hashes, URDF/MJCF references, and calibration
reports needed to reproduce the simulation. Do not claim sim-to-real transfer
until the measured parameters and their uncertainty are linked to a config.

## 3. Validate locally

Use the laptop for configuration validation, lightweight MuJoCo scenes,
visualization, unit tests, and controller logic that does not command hardware:

```bash
bash scripts/preflight.sh local
.mamba-env/bin/python -m pytest -q
.mamba-env/bin/python -m src.experiment --config configs/sim.yaml --dry-run
```

The local stage also checks that the current `codex/<task>` branch has a
matching `docs/tasks/<task>.md` brief and that the literature-source policy is
valid. It should prove the config contract and observation/action shapes before
consuming server GPU time.

## 4. Run simulation on the server

Connect with VS Code Remote-SSH or `ssh research-gpu`. Keep the server's main
checkout stable and use a branch-specific worktree under the `gbu` home:

```bash
ssh research-gpu
repo=/home/gbu/research/Compliant-Force-controlled-Robot-Project
wt=/home/gbu/research/worktrees/codex-<task-name>
cd "$repo"
git fetch origin <branch-name>
git worktree add "$wt" origin/<branch-name>
cd "$wt"
```

If the worktree already exists, update it only after checking it is clean:

```bash
git status --short --branch
git pull --ff-only
```

The common user-space environment is
`/home/gbu/miniforge3/envs/compliant-force-robot`. From the worktree root,
validate the exact commit and configuration before running a simulation:

```bash
git log -1 --oneline
/home/gbu/miniforge3/envs/compliant-force-robot/bin/python \
  -m src.experiment --config configs/sim.yaml --dry-run
/home/gbu/miniforge3/envs/compliant-force-robot/bin/python \
  -m src.mujoco_smoke --steps 100
```

For the contact-loss robustness matrix, use the committed YAML so the axes,
controller, safety thresholds, and seed are part of the run contract:

```bash
python -m src.contact_loss_recovery_matrix \
  --config configs/contact_loss_recovery_matrix.yaml \
  --output /tmp/contact-loss-recovery-matrix.json
```

The matrix JSON must be copied with the run manifest when it becomes a server
artifact. Its `failure_count` is evidence, not a reason to discard cases.

For the variable-compliance peg-in-hole matrix, use the same config-driven
entry point locally or in a user-space server worktree:

```bash
.mamba-env/bin/python -m src.variable_compliance_matrix \
  --config configs/variable_compliance_peg.yaml --dry-run
.mamba-env/bin/python -m src.variable_compliance_matrix \
  --config configs/variable_compliance_peg.yaml --max-cases 1 \
  --run-id variable-peg-smoke
```

The four matrix axes are strategy, seed, initial lateral offset, and friction.
Each case is retained in `results.json`, including failures, and the manifest
records the current Git commit, Python package snapshot, and optional Slurm job
ID. `--dry-run` creates no artifact directory.

Run `bash scripts/preflight.sh server` only when a scheduler is available; on
the current shared workstation it intentionally reports `slurm=unavailable`.

This host currently has no verified Slurm scheduler. Until the lab provides an
approved scheduler or reservation procedure, do not run long jobs or occupy a
GPU directly. Once Slurm is available, submit only through
`bash scripts/submit-slurm.sh train` or `eval`, with all resource variables set.

Simulation jobs should write only to `artifacts/<run-id>` and record the config,
metrics, simulator version, seed, and job ID. Matrix runs additionally create
`cases/<index>-<variant>/` directories for learned variants. Each such directory
contains the complete dataset, episode-safe train/test split, and bounded policy
checkpoint (`dataset.npz`, `train.npz`, `test.npz`, and `policy.npz`), while
`results.json` references those files with paths relative to the run directory.
This makes an independent checkpoint reload or archive verification possible
after copying the run directory. Keep large videos and checkpoints on the server
until evaluation is complete.

## 5. Collect data, train, and evaluate

Use the same committed config and observation/action contract for data
collection, training, validation, and held-out evaluation. Separate training,
validation, and test seeds or environments; record leakage checks, checkpoint
selection, and all failed runs. Add one transparent baseline before introducing
new policy components, then report ablations for sensors, dynamics
randomization, controller gains, and latency where relevant.

## 6. Evaluate and archive

Evaluate a checkpoint with a separate config and record aggregate metrics plus
per-seed results. Before copying results, preview the transfer:

```bash
bash scripts/sync-results.sh --dry-run <run-id>
bash scripts/sync-results.sh <run-id>
```

The script copies from the server with resumable, checksum-verified `rsync` to
`/mnt/research-data`. Its default source is the server's main checkout; when a
branch worktree produced the run, point it at that worktree explicitly:

```bash
REMOTE_ARTIFACT_ROOT=/home/gbu/research/worktrees/codex-<task-name>/artifacts \
  bash scripts/sync-results.sh --dry-run <run-id>
REMOTE_ARTIFACT_ROOT=/home/gbu/research/worktrees/codex-<task-name>/artifacts \
  bash scripts/sync-results.sh <run-id>
```

The script refuses to run unless `/mnt/research-data` is mounted and writable,
then writes `SHA256SUMS` after a successful copy. Source code is synchronized
with GitHub; the mechanical drive is for large artifacts and data only. The
checksum list intentionally excludes `SHA256SUMS` itself, so it can be checked
directly with `(cd /mnt/research-data/<project>/<run-id> && sha256sum -c SHA256SUMS)`.

## 7. Prepare supervised hardware validation

Do not add a real robot command until these fields are documented in the
experiment record:

- robot model, firmware, communication path, and joint limits;
- force/torque sensor model, frame convention, calibration procedure, and rate;
- controller mode, torque/velocity limits, watchdog, emergency stop, and safe pose;
- operator, workspace exclusion zone, and a dry-run procedure with motors disabled.

First replay recorded trajectories, then use low-gain, low-speed commands with a
human operator and an independent stop path. Compare real observations against
the simulation contract before enabling learning or adaptation.

## 8. Iterate, write, and release

For each change, record the Git commit, environment lock, config, seed, run IDs,
metrics, failures, and rollback decision. Generate figures and tables directly
from versioned metrics; keep equation definitions tied to the observation,
action, and controller interfaces. Promote a model from simulation to hardware
only after it passes offline evaluation, bounded simulation tests, and a
supervised hardware checklist. A paper-ready result should be reproducible from
the committed config and the archived run directory, with limitations and
negative results retained alongside successful runs.
