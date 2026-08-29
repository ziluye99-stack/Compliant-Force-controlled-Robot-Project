#!/usr/bin/env python3
"""Check the repository contract for a reproducible research release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "docs/PROJECT_VISION.md",
    "docs/workflow.md",
    "docs/release-checklist.md",
    "docs/experiments/README.md",
    "docs/literature/README.md",
    "environment.lock.txt",
    "configs/platform_neutral_interface.yaml",
)

REQUIRED_MARKERS = (
    "## Evidence bundle",
    "## Literature and claims",
    "## Hardware boundary",
    "## Run handoff",
    "run_id:",
    "git_commit:",
    "known_limitations:",
)


def validate_release_contract(root: Path) -> dict[str, Any]:
    issues: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing required release input: {relative}")

    checklist = root / "docs/release-checklist.md"
    if checklist.is_file():
        text = checklist.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                issues.append(f"release checklist missing marker: {marker}")

    return {
        "root": str(root),
        "valid": not issues,
        "issues": issues,
        "checked_files": list(REQUIRED_FILES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    report = validate_release_contract(args.root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
