#!/usr/bin/env bash
#SBATCH --job-name=force-eval
#SBATCH --output=artifacts/slurm-%x-%j.out
#SBATCH --error=artifacts/slurm-%x-%j.err

set -euo pipefail
cd "$HOME/research/Compliant-Force-controlled-Robot-Project"
mkdir -p artifacts
[[ -n "${SLURM_JOB_ID:-}" ]] || { echo "This template must run under Slurm." >&2; exit 1; }
micromamba run -n compliant-force-robot python -m src.experiment --config configs/sim.yaml
