#!/usr/bin/env python3
"""Validate the versioned literature-source policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_PRIMARY = {
    "wos_sci",
    "robotics_journals",
    "robotics_conferences",
    "nature_science",
    "chinese_databases",
}
REQUIRED_DISCOVERY = {
    "semantic_scholar",
    "openalex",
    "crossref",
    "arxiv",
}


def validate_policy(path: Path) -> dict[str, Any]:
    issues: list[str] = []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised through CLI errors
        return {"path": str(path), "valid": False, "issues": [f"cannot read YAML: {exc}"]}
    if not isinstance(payload, dict):
        return {"path": str(path), "valid": False, "issues": ["top level must be a mapping"]}
    if payload.get("policy_version") != 1:
        issues.append("policy_version must be 1")

    def source_ids(key: str) -> set[str]:
        entries = payload.get(key)
        if not isinstance(entries, list):
            issues.append(f"{key} must be a list")
            return set()
        ids: set[str] = set()
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                issues.append(f"{key}[{index}] must be a mapping")
                continue
            source_id = entry.get("id")
            if not isinstance(source_id, str) or not source_id:
                issues.append(f"{key}[{index}] has no id")
            else:
                ids.add(source_id)
            for field in ("name", "class", "access"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    issues.append(f"{key}[{index}] missing {field}")
        return ids

    primary = source_ids("primary_full_text")
    discovery = source_ids("discovery_and_cross_check")
    for source_id in sorted(REQUIRED_PRIMARY - primary):
        issues.append(f"missing primary source: {source_id}")
    for source_id in sorted(REQUIRED_DISCOVERY - discovery):
        issues.append(f"missing discovery source: {source_id}")
    rules = payload.get("evidence_rules")
    if not isinstance(rules, list) or len(rules) < 4:
        issues.append("evidence_rules must contain at least four rules")
    axes = payload.get("project_axes")
    if not isinstance(axes, list) or not axes:
        issues.append("project_axes must be a non-empty list")
    return {"path": str(path), "valid": not issues, "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path("configs/literature_sources.yaml"))
    args = parser.parse_args()
    report = validate_policy(args.path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
