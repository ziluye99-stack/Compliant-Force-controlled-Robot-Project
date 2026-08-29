# Compliant Force-Controlled Robot Project

Reproducible research scaffold for compliant force-control experiments. The first implementation stage provides experiment metadata, simulator-ready configuration, Slurm-safe job submission, and verified artifact synchronization. It intentionally does not assume a robot model, force sensor, controller, or training algorithm.

## Workspace roles

| Location | Role |
| --- | --- |
| Laptop | Code editing, lightweight MuJoCo validation, visualization, and future supervised hardware debugging |
| `research-gpu` | Slurm-submitted simulation, training, evaluation, and large artifact generation |
| `/mnt/research-data` | Local archival destination for validated result copies |
| GitHub | Source, configs, documentation, and small text metrics only |

## Quick start

1. Create the local environment with `micromamba create -y -p .mamba-env -f environment.yml` and `.mamba-env/bin/pip install -e .[dev]`, or create the server environment from `environment.yml`.
2. Run `.mamba-env/bin/python -m src.experiment --config configs/sim.yaml --dry-run`.
3. Run `bash scripts/preflight.sh local` before local validation.
4. After server access is authorized, run `bash scripts/preflight.sh server`.
5. Set the required Slurm variables and submit with `bash scripts/submit-slurm.sh train`.
6. Archive finished results with `bash scripts/sync-results.sh --dry-run <run-id>` before an actual sync.

If `bash scripts/preflight.sh server` reports `slurm=unavailable`, the host has
visible GPUs but no Slurm client or scheduler configuration. Do not start
training directly on that shared host; obtain the lab's scheduler node or an
explicit resource-sharing policy first.

## Experiment contract

Each run has a unique `run_id`, a YAML configuration, and a server-side artifact directory. The run manifest records a random seed, Git revision, dependency snapshot, Slurm job ID, and result path. Generated artifacts never enter Git.

## Server policy

The project uses only the `gbu` user space on the shared server. Jobs must request their resources through Slurm. The scripts refuse to submit without explicit account, partition, GPU, CPU, memory, and time settings.
