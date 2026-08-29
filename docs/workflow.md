# Research Workflow

This repository defines the common path from an experiment idea to simulation,
training, evaluation, and supervised hardware validation. Robot-specific
drivers and control limits must be supplied before the hardware stages are
enabled.

## 1. Design the experiment

Start with `docs/experiments/template.md`. State one question, one hypothesis,
the baseline, independent variables, controlled variables, success metrics, and
hardware safety constraints. Create or update a YAML file under `configs/` and
review it before running code.

Every run must have a unique `run_id`, fixed seed, committed Git revision, and
an artifact directory. Do not put raw data, checkpoints, videos, or credentials
in Git.

## 2. Validate locally

Use the laptop for configuration validation, lightweight MuJoCo scenes,
visualization, unit tests, and controller logic that does not command hardware:

```bash
bash scripts/preflight.sh local
.mamba-env/bin/python -m pytest -q
.mamba-env/bin/python -m src.experiment --config configs/sim.yaml --dry-run
```

The local stage should prove the config contract and observation/action shapes
before consuming server GPU time.

## 3. Run simulation on the server

Connect with VS Code Remote-SSH or `ssh research-gpu`. The server project uses
`/home/gbu/miniforge3/envs/compliant-force-robot` for the common MuJoCo
environment. Run `bash scripts/preflight.sh server` first.

This host currently has no verified Slurm scheduler. Until the lab provides an
approved scheduler or reservation procedure, do not run long jobs or occupy a
GPU directly. Once Slurm is available, submit only through
`bash scripts/submit-slurm.sh train` or `eval`, with all resource variables set.

Simulation jobs should write only to `artifacts/<run-id>` and record the config,
metrics, simulator version, seed, and job ID. Keep large videos and checkpoints
on the server until evaluation is complete.

## 4. Evaluate and archive

Evaluate a checkpoint with a separate config and record aggregate metrics plus
per-seed results. Before copying results, preview the transfer:

```bash
bash scripts/sync-results.sh --dry-run <run-id>
bash scripts/sync-results.sh <run-id>
```

The script copies from the server with resumable, checksum-verified `rsync` to
`/mnt/research-data`. Source code is synchronized with GitHub; the mechanical
drive is for large artifacts and data only.

## 5. Prepare supervised hardware validation

Do not add a real robot command until these fields are documented in the
experiment record:

- robot model, firmware, communication path, and joint limits;
- force/torque sensor model, frame convention, calibration procedure, and rate;
- controller mode, torque/velocity limits, watchdog, emergency stop, and safe pose;
- operator, workspace exclusion zone, and a dry-run procedure with motors disabled.

First replay recorded trajectories, then use low-gain, low-speed commands with a
human operator and an independent stop path. Compare real observations against
the simulation contract before enabling learning or adaptation.

## 6. Iterate and release

For each change, record the Git commit, environment lock, config, seed, run IDs,
metrics, failures, and rollback decision. Promote a model from simulation to
hardware only after it passes offline evaluation, bounded simulation tests,
and a supervised hardware checklist. A paper-ready result should be reproducible
from the committed config and the archived run directory.
