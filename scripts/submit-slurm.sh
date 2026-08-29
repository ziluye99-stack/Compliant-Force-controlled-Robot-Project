#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"
if [[ "$target" != "train" && "$target" != "eval" ]]; then
  echo "Usage: $0 {train|eval}" >&2
  exit 2
fi

if ! command -v sbatch >/dev/null; then
  echo "Slurm is unavailable on this host (sbatch not found); refusing to run a direct job." >&2
  exit 2
fi

for required in SLURM_ACCOUNT SLURM_PARTITION SLURM_GPUS SLURM_CPUS SLURM_MEM SLURM_TIME; do
  if [[ -z "${!required:-}" ]]; then
    echo "Set $required before submitting; shared-server jobs require explicit resources." >&2
    exit 1
  fi
done

script="slurm/${target}.sbatch"
[[ -f "$script" ]] || { echo "Missing template: $script" >&2; exit 1; }
sbatch --account="$SLURM_ACCOUNT" --partition="$SLURM_PARTITION" --gpus="$SLURM_GPUS" --cpus-per-task="$SLURM_CPUS" --mem="$SLURM_MEM" --time="$SLURM_TIME" "$script"
