#!/usr/bin/env python3
"""Create a provenance-aware paper-note skeleton for an authorized PDF."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from pathlib import Path


EVIDENCE_STATUSES = ("full-text", "accepted-manuscript", "preprint", "metadata-only")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_note(args: argparse.Namespace, digest: str) -> str:
    return f"""# Paper Note: {args.short_title}

## Bibliographic record

- Title: {args.title}
- Authors: {args.authors}
- Venue and year: {args.venue_year}
- DOI: {args.doi or 'not supplied'}
- Publisher URL: {args.publisher_url or 'not supplied'}
- Preprint or code URL: {args.preprint_url or 'not supplied'}
- Discovery source and access date: {args.discovery_source}; {args.access_date}
- Full-text access route (publisher, school portal, repository, or preprint): {args.full_text_route}
- Full-text file and SHA-256: `{args.pdf}`; `{digest}`
- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): {args.evidence_status}

## Translation and terminology

- Abstract translation: <complete after reading the PDF>
- Important terms and preferred Chinese/English wording: <complete after reading the PDF>
- Sentences or equations needing a second pass: <complete after reading the PDF>

## Technical digest

- Problem and claimed gap: <complete after reading the PDF>
- Method and key equations: <complete after reading the PDF>
- Sensors, observations, actions, and controller interface: <complete after reading the PDF>
- Simulation platform and task details: <complete after reading the PDF>
- Dataset or demonstrations: <complete after reading the PDF>
- Training procedure and compute: <complete after reading the PDF>
- Reproduction-critical constants and missing details: <complete after reading the PDF>

## Experimental design analysis

- Baselines and whether comparisons are fair: <complete after reading the PDF>
- Metrics and statistical treatment: <complete after reading the PDF>
- Ablations and what they establish: <complete after reading the PDF>
- Real-robot evidence and sim-to-real procedure: <complete after reading the PDF>
- Failure cases and missing controls: <complete after reading the PDF>
- Evidence locations (section/table/figure/equation): <complete after reading the PDF>

## Assessment

- Strengths: <complete after reading the PDF>
- Weaknesses and hidden assumptions: <complete after reading the PDF>
- Reproducibility: what is available and what is missing: <complete after reading the PDF>
- Relevance to the project vision: <complete after reading the PDF>
- Follow-up experiment in MuJoCo: <complete after reading the PDF>
- Candidate extension or research gap: <complete after reading the PDF>

## Actions

- [ ] Add metadata to the literature index/Zotero
- [x] Save the PDF outside Git
- [ ] Reproduce the smallest reported result
- [ ] Create or update a project config
- [ ] Link this note from an experiment record
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--short-title", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", required=True)
    parser.add_argument("--venue-year", required=True)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--discovery-source", required=True)
    parser.add_argument("--full-text-route", required=True)
    parser.add_argument("--doi")
    parser.add_argument("--publisher-url")
    parser.add_argument("--preprint-url")
    parser.add_argument("--access-date", default=dt.date.today().isoformat())
    parser.add_argument("--evidence-status", choices=EVIDENCE_STATUSES, default="full-text")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.pdf = args.pdf.expanduser().resolve()
    if not args.pdf.is_file() or args.pdf.suffix.lower() != ".pdf":
        parser.error(f"authorized PDF does not exist or is not a PDF: {args.pdf}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite existing note: {args.output}")
    args.output.write_text(render_note(args, sha256(args.pdf)), encoding="utf-8")
    print(f"created {args.output}")
    print(f"pdf_sha256 {sha256(args.pdf)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
