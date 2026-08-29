#!/usr/bin/env bash
set -euo pipefail

# Run only after logging in as gbu. This script stays entirely in the user home.
project="Compliant-Force-controlled-Robot-Project"
project_root="$HOME/research/$project"
cache_root="${SCRATCH:-$HOME/.cache}/$project"

mkdir -p "$project_root" "$project_root/artifacts" "$cache_root"
export XDG_CACHE_HOME="$cache_root"
export PIP_CACHE_DIR="$cache_root/pip"

if ! command -v micromamba >/dev/null; then
  echo "Install Micromamba in your user directory first; do not use sudo or modify the shared Python." >&2
  exit 1
fi

micromamba env create -f "$project_root/environment.yml" -n compliant-force-robot || micromamba env update -f "$project_root/environment.yml" -n compliant-force-robot
micromamba run -n compliant-force-robot python -m pip freeze > "$project_root/environment.lock.txt"
echo "Server environment prepared under $HOME only."
