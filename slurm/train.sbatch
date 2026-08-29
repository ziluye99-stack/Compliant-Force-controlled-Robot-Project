#!/usr/bin/env bash
# Resource values are injected by scripts/submit-slurm.sh and must not be hard-coded.
#SBATCH --job-name=force-train
#SBATCH --output=artifacts/slurm-%x-%j.out
#SBATCH --error=artifacts/slurm-%x-%j.err

set -euo pipefail
cd "$HOME/research/Compliant-Force-controlled-Robot-Project"
mkdir -p artifacts
[[ -n "${SLURM_JOB_ID:-}" ]] || { echo "This template must run under Slurm." >&2; exit 1; }
micromamba run -n compliant-force-robot python -m src.experiment --config configs/train.yaml
