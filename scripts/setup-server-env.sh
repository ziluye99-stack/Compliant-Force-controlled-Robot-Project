#!/usr/bin/env bash
set -euo pipefail

# Run only after logging in as gbu. This script stays entirely in the user home.
project="Compliant-Force-controlled-Robot-Project"
project_root="$HOME/research/$project"
cache_root="${SCRATCH:-$HOME/.cache}/$project"

mkdir -p "$project_root" "$project_root/artifacts" "$cache_root"
export XDG_CACHE_HOME="$cache_root"
export PIP_CACHE_DIR="$cache_root/pip"

env_tool=""
if command -v micromamba >/dev/null; then
  env_tool="micromamba"
elif [[ -x "$HOME/miniforge3/bin/mamba" ]]; then
  env_tool="$HOME/miniforge3/bin/mamba"
elif [[ -x "$HOME/miniforge3/bin/conda" ]]; then
  env_tool="$HOME/miniforge3/bin/conda"
elif [[ -x "$HOME/miniconda3/bin/conda" ]]; then
  env_tool="$HOME/miniconda3/bin/conda"
else
  echo "No user-space Micromamba/Mamba/Conda found; do not use sudo or modify the shared Python." >&2
  exit 1
fi

"$env_tool" env create -f "$project_root/environment.yml" -n compliant-force-robot || "$env_tool" env update -f "$project_root/environment.yml" -n compliant-force-robot
"$env_tool" run -n compliant-force-robot python -m pip freeze > "$project_root/environment.lock.txt"
echo "Server environment prepared under $HOME only."
