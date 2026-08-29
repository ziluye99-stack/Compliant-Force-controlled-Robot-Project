#!/usr/bin/env python3
"""Check that a focused Codex branch has a corresponding task brief."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_MARKERS = (
    "docs/PROJECT_VISION.md",
    "Read `docs/PROJECT_VISION.md`",
    "Stage gate",
    "Expected artifact",
    "## Verification",
)


def current_branch(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_branch_task(root: Path, branch: str | None = None) -> dict[str, Any]:
    branch = branch or current_branch(root)
    if branch in {"main", "master"}:
        return {"branch": branch, "task": None, "valid": True, "issues": []}
    if not branch.startswith("codex/"):
        return {
            "branch": branch,
            "task": None,
            "valid": False,
            "issues": ["focused work must use a codex/<task-name> branch"],
        }
    task_name = branch.removeprefix("codex/")
    task_path = root / "docs" / "tasks" / f"{task_name}.md"
    issues: list[str] = []
    if not task_path.is_file():
        issues.append(f"missing task brief: {task_path}")
    else:
        text = task_path.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                issues.append(f"task brief missing marker: {marker}")
        if "Project priority" not in text and "Project priorities" not in text:
            issues.append("task brief missing marker: Project priority")
        if f"`codex/{task_name}`" not in text and f"codex/{task_name}" not in text:
            issues.append("task brief does not name the current branch")
    return {"branch": branch, "task": str(task_path), "valid": not issues, "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--branch")
    args = parser.parse_args()
    report = validate_branch_task(args.root.resolve(), args.branch)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
