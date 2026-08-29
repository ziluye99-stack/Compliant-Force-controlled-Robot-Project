#!/usr/bin/env bash
set -euo pipefail

# Read-only inventory for the shared workstation. This intentionally succeeds
# when Slurm is absent so it can be used before deciding whether a job is safe.
ssh research-gpu 'set -e
  printf "host=%s user=%s os=" "$(hostname)" "$(id -un)"
  . /etc/os-release
  printf "%s\\n" "$PRETTY_NAME"

  printf "gpu:\\n"
  if command -v nvidia-smi >/dev/null; then
    nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader
  else
    printf "unavailable (nvidia-smi not found)\\n"
  fi

  printf "disk:\\n"
  df -h "$HOME"

  printf "project=%s\\n" "$HOME/research/Compliant-Force-controlled-Robot-Project"
  printf "environments:\\n"
  for env in \
    "$HOME/miniforge3/envs/compliant-force-robot" \
    "$HOME/miniforge3/envs/lerobot_rm65" \
    "$HOME/miniconda3/envs/pytorch"; do
    if [[ -x "$env/bin/python" ]]; then
      printf "%s: " "$env"
      "$env/bin/python" -c "import sys; print(sys.version.split()[0])"
    fi
  done

  if command -v sinfo >/dev/null && command -v squeue >/dev/null; then
    printf "scheduler=slurm\\n"
    sinfo -h -o "%P %G %C"
    squeue -u "$USER"
  else
    printf "scheduler=unavailable\\n"
    printf "policy=read-only checks and short coordinated smoke tests only; no direct training\\n"
  fi
'
