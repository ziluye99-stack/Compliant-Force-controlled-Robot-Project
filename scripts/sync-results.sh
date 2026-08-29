#!/usr/bin/env bash
set -euo pipefail

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
  shift
fi
run_id="${1:-}"
if [[ -z "$run_id" ]]; then
  echo "Usage: $0 [--dry-run] <run-id>" >&2
  exit 2
fi

drive="/mnt/research-data"
project="Compliant-Force-controlled-Robot-Project"
remote_artifact_root="${REMOTE_ARTIFACT_ROOT:-~/research/$project/artifacts}"
source_path="research-gpu:${remote_artifact_root%/}/$run_id/"
destination="$drive/$project/$run_id/"

if ! mountpoint -q "$drive"; then
  echo "Research drive is not mounted at $drive; refusing to sync." >&2
  exit 1
fi
if [[ ! -w "$drive" ]]; then
  echo "Research drive is not writable: $drive" >&2
  exit 1
fi

mkdir -p "$destination"
options=(--archive --partial --append-verify --checksum --human-readable --info=progress2)
if "$dry_run"; then
  options+=(--dry-run)
fi
rsync "${options[@]}" "$source_path" "$destination"
if ! "$dry_run"; then
  # Exclude the manifest itself so `sha256sum -c SHA256SUMS` is stable.
  (cd "$destination" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum) > "$destination/SHA256SUMS"
  echo "Archived $run_id to $destination"
fi
