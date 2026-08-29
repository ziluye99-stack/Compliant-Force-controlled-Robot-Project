#!/usr/bin/env python3
"""Validate structured literature notes before they become design evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "Title",
    "Authors",
    "Venue and year",
    "DOI",
    "Discovery source and access date",
    "Full-text access route",
    "Full-text file and SHA-256",
    "Evidence status",
)
REQUIRED_SECTIONS = (
    "Translation and terminology",
    "Technical digest",
    "Experimental design analysis",
    "Assessment",
    "Follow-up experiment in MuJoCo",
)
EVIDENCE_STATUSES = frozenset(
    {"full-text", "accepted-manuscript", "preprint", "metadata-only"}
)


def _section_blocks(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1).strip()] = text[match.end() : end].strip()
    return blocks


def _field_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if match:
            values[match.group(1).strip()] = match.group(2).strip()
    return values


def _is_placeholder(value: str) -> bool:
    return not value or value.startswith("<") or value.endswith(">")


def _value_for_prefix(fields: dict[str, str], prefix: str) -> str:
    for label, value in fields.items():
        if label == prefix or label.startswith(prefix + " "):
            return value
    return ""


def _full_text_path(value: str) -> Path | None:
    match = re.search(r"`?(/[^`;]+\.pdf)`?", value)
    return Path(match.group(1)) if match else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_note(
    path: Path,
    require_full_text: bool = False,
    require_primary_evidence: bool = False,
    verify_files: bool = False,
) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fields = _field_values(text)
    sections = _section_blocks(text)
    issues: list[str] = []
    for field in REQUIRED_FIELDS:
        value = _value_for_prefix(fields, field)
        if _is_placeholder(value):
            issues.append(f"missing field: {field}")
    for section in REQUIRED_SECTIONS:
        content = sections.get(section, "")
        if _is_placeholder(content):
            issues.append(f"missing section content: {section}")

    evidence_status = _value_for_prefix(fields, "Evidence status").lower()
    if not _is_placeholder(evidence_status) and evidence_status not in EVIDENCE_STATUSES:
        valid_statuses = ", ".join(sorted(EVIDENCE_STATUSES))
        issues.append(f"invalid evidence status: {evidence_status}; expected one of {valid_statuses}")
    if require_full_text and (evidence_status == "metadata-only" or _is_placeholder(evidence_status)):
        issues.append("full-text evidence is required for this gate")
    if require_primary_evidence and evidence_status != "full-text":
        issues.append("primary publisher or authorized-portal full-text evidence is required for this gate")

    file_status = "not-checked"
    file_path = _full_text_path(fields.get("Full-text file and SHA-256", ""))
    expected_hash_match = re.search(r"\b([0-9a-fA-F]{64})\b", _value_for_prefix(fields, "Full-text file and SHA-256"))
    if verify_files:
        if file_path is None:
            issues.append("full-text file path is missing or is not an absolute PDF path")
            file_status = "missing-path"
        elif not file_path.is_file():
            issues.append(f"full-text file does not exist: {file_path}")
            file_status = "missing-file"
        elif expected_hash_match is None:
            issues.append("full-text SHA-256 is missing or malformed")
            file_status = "missing-hash"
        else:
            actual_hash = _sha256(file_path)
            if actual_hash.lower() != expected_hash_match.group(1).lower():
                issues.append(f"SHA-256 mismatch for {file_path}")
                file_status = "hash-mismatch"
            else:
                file_status = "verified"

    return {
        "path": str(path),
        "title": fields.get("Title"),
        "evidence_status": evidence_status,
        "full_text_file_status": file_status,
        "issues": issues,
        "valid": not issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown notes; defaults to docs/literature/notes/*.md")
    parser.add_argument("--require-full-text", action="store_true", help="Fail metadata-only notes")
    parser.add_argument(
        "--require-primary-evidence",
        action="store_true",
        help="Require a publisher or authorized-portal full-text record, not a manuscript or preprint",
    )
    parser.add_argument("--verify-files", action="store_true", help="Check referenced PDF files and SHA-256")
    args = parser.parse_args()
    paths = args.paths or sorted(Path("docs/literature/notes").glob("*.md"))
    if not paths:
        parser.error("no note files found")
    reports = [
        validate_note(
            path,
            require_full_text=args.require_full_text,
            require_primary_evidence=args.require_primary_evidence,
            verify_files=args.verify_files,
        )
        for path in paths
    ]
    print(json.dumps({"note_count": len(reports), "valid_count": sum(report["valid"] for report in reports), "notes": reports}, ensure_ascii=False, indent=2))
    return 0 if all(report["valid"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
