#!/usr/bin/env python3
"""Validate three locally downloaded portal PDFs and write a hash manifest.

This is a local handoff check only. It never logs in to a portal, uploads a
file, or adds a PDF to Git. Paths may be absolute or relative to ``--root``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


AXES = (
    ("admittance", "--admittance"),
    ("impedance_hybrid", "--impedance-hybrid"),
    ("humanoid_multicontact", "--humanoid-multicontact"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_pdf(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"path": str(path)}
    if not path.is_file():
        record["status"] = "missing"
        return record
    size = path.stat().st_size
    record["size_bytes"] = size
    if size == 0:
        record["status"] = "empty"
        return record
    with path.open("rb") as handle:
        magic = handle.read(5)
    if magic != b"%PDF-":
        record["status"] = "not_pdf"
        return record
    record.update({"status": "ok", "sha256": sha256(path)})
    return record


def resolve(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def build_manifest(root: Path, paths: dict[str, Path]) -> dict[str, Any]:
    records = {axis: inspect_pdf(path) for axis, path in paths.items()}
    unique_paths = [str(path.resolve()) for path in paths.values()]
    duplicate_paths = sorted({path for path in unique_paths if unique_paths.count(path) > 1})
    valid = all(record["status"] == "ok" for record in records.values()) and not duplicate_paths
    return {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "root": str(root),
        "valid": valid,
        "duplicate_paths": duplicate_paths,
        "papers": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/mnt/research-data/literature/pdfs"))
    for axis, option in AXES:
        parser.add_argument(option, required=True, help=f"PDF for the {axis} axis")
    parser.add_argument("--output", type=Path, help="Write the JSON manifest here")
    args = parser.parse_args()

    root = args.root.expanduser()
    paths = {axis: resolve(root, getattr(args, option[2:].replace("-", "_"))) for axis, option in AXES}
    manifest = build_manifest(root, paths)
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if manifest["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
