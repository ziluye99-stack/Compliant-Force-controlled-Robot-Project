# Research Workspace Guidance

## Safety and Ownership

- Treat this repository as a research scaffold. Do not add hardware drivers, robot commands, or autonomous deployment behavior until a specific platform and safety procedure are supplied.
- Never commit credentials, private keys, raw data, checkpoints, videos, or generated experiment artifacts.
- Server workloads must use Slurm allocation commands. Do not train on login nodes, use `sudo`, change shared system dependencies, target GPUs manually, or terminate processes owned by other users.

## Reproducibility

- Every experiment starts from a YAML config and records its Git commit, random seed, Python package snapshot, Slurm job ID, and artifact path.
- Keep source code, configs, documentation, and Slurm templates in Git. Keep large artifacts in the server artifact directory and synchronize verified copies to the research drive.
- Run `scripts/preflight.sh` before submitting a job and `scripts/sync-results.sh --dry-run <run-id>` before copying results locally.

## Commands

- `python -m src.experiment --config configs/sim.yaml --dry-run` validates a config without starting a simulator or training job.
- `bash scripts/preflight.sh local` checks the laptop environment.
- `bash scripts/preflight.sh server` runs read-only checks through the `research-gpu` SSH alias after server access is configured.
- `bash scripts/submit-slurm.sh train` submits the training template only when the required Slurm environment variables are explicitly set.
