#!/usr/bin/env bash
set -euo pipefail

mode="${1:-local}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-$root/.mamba-env/bin/python}"
[[ -x "$python_bin" ]] || python_bin="${PYTHON_BIN:-$root/.venv/bin/python}"
[[ -x "$python_bin" ]] || python_bin="${PYTHON_BIN:-python}"

require_command() {
  command -v "$1" >/dev/null || { echo "Missing required command: $1" >&2; exit 1; }
}

if [[ "$mode" == "local" ]]; then
  require_command git
  require_command "$python_bin"
  require_command rsync
  git -C "$root" status --short --branch
  (cd "$root" && "$python_bin" scripts/check-branch-task.py >/dev/null)
  (cd "$root" && "$python_bin" scripts/check-literature-sources.py >/dev/null)
  (cd "$root" && "$python_bin" -m src.experiment --config configs/sim.yaml --dry-run >/dev/null)
  (cd "$root" && "$python_bin" -m src.mujoco_smoke --steps 10 >/dev/null)
  echo "Local preflight passed."
elif [[ "$mode" == "server" ]]; then
  require_command ssh
  ssh research-gpu 'set -e;
    printf "host=%s user=%s\\n" "$(hostname)" "$(id -un)";
    printf "gpu:\\n";
    nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader;
    printf "home:\\n";
    df -h "$HOME";
    if command -v sinfo >/dev/null && command -v squeue >/dev/null; then
      printf "slurm:\\n";
      sinfo -h -o "%P %G %C";
      squeue -u "$USER";
    else
      printf "slurm=unavailable (sinfo/squeue not found)\\n";
      exit 2;
    fi'
  echo "Server read-only preflight passed."
else
  echo "Usage: $0 {local|server}" >&2
  exit 2
fi
