#!/usr/bin/env bash
set -euo pipefail

dry_run=false
remote_artifact_root="${REMOTE_ARTIFACT_ROOT:-}"
run_id=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      dry_run=true
      shift
      ;;
    --remote-artifact-root)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "--remote-artifact-root requires a path" >&2
        exit 2
      fi
      remote_artifact_root="$2"
      shift 2
      ;;
    --remote-artifact-root=*)
      remote_artifact_root="${1#*=}"
      if [[ -z "$remote_artifact_root" ]]; then
        echo "--remote-artifact-root requires a path" >&2
        exit 2
      fi
      shift
      ;;
    --)
      shift
      if [[ $# -gt 0 ]]; then
        run_id="$1"
        shift
      fi
      ;;
    -* )
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--dry-run] [--remote-artifact-root <path>] <run-id>" >&2
      exit 2
      ;;
    *)
      if [[ -n "$run_id" ]]; then
        echo "Only one <run-id> may be supplied" >&2
        exit 2
      fi
      run_id="$1"
      shift
      ;;
  esac
done
if [[ -z "$run_id" ]]; then
  echo "Usage: $0 [--dry-run] [--remote-artifact-root <path>] <run-id>" >&2
  exit 2
fi

drive="/mnt/research-data"
project="Compliant-Force-controlled-Robot-Project"
if [[ -z "$remote_artifact_root" ]]; then
  remote_artifact_root="~/research/$project/artifacts"
fi
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
