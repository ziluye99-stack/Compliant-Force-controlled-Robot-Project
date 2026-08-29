#!/usr/bin/env python3
"""Query public scholarly metadata and write a provenance-preserving result set.

This tool is for discovery only.  It does not download papers or bypass a
publisher, CNKI, or university-portal access control.  Full-text evidence must
still be obtained through an authorized route and recorded in a paper note.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_RATE_LIMIT_RETRIES = 1
DEFAULT_MAX_RETRY_DELAY = 5.0


VENUE_PRIORITY = (
    "science robotics",
    "nature machine intelligence",
    "nature",
    "science",
    "ieee transactions on robotics",
    "international journal of robotics research",
    "ijrr",
    "robotics and automation letters",
    "ral",
    "rss",
    "corl",
    "icra",
    "iros",
    "automatica",
    "ieee/asme transactions on mechatronics",
)


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = doi.removesuffix(".")
    return doi or None


def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def publication_year(item: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.match(r"(19|20)\d{2}", value)
            if match:
                return int(match.group(0))
    return None


def venue_score(venue: str | None) -> int:
    normalized = normalize_title(venue)
    for index, preferred in enumerate(VENUE_PRIORITY):
        if normalize_title(preferred) in normalized:
            return len(VENUE_PRIORITY) - index
    return 0


def _authors_openalex(item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for authorship in item.get("authorships", []):
        author = authorship.get("author", {})
        if author.get("display_name"):
            names.append(str(author["display_name"]))
    return names


def _authors_crossref(item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for author in item.get("author", []):
        given = str(author.get("given", "")).strip()
        family = str(author.get("family", "")).strip()
        name = " ".join(part for part in (given, family) if part)
        if name:
            names.append(name)
    return names


def from_openalex(item: dict[str, Any]) -> dict[str, Any]:
    location = item.get("primary_location") or {}
    source = location.get("source") or {}
    oa = item.get("open_access") or {}
    best_oa = item.get("best_oa_location") or {}
    venue = source.get("display_name")
    return {
        "title": (item.get("title") or "").strip(),
        "doi": normalize_doi(item.get("doi")),
        "venue": venue,
        "year": publication_year(item, "publication_year", "publication_date"),
        "authors": _authors_openalex(item),
        "citations": int(item.get("cited_by_count") or 0),
        "publisher_url": location.get("landing_page_url"),
        "open_access": bool(oa.get("is_oa")),
        "pdf_url": best_oa.get("pdf_url"),
        "discovery_sources": ["OpenAlex"],
        "evidence_status": "metadata-only",
    }


def from_crossref(item: dict[str, Any]) -> dict[str, Any]:
    dates = item.get("published-print") or item.get("published-online") or item.get("issued") or {}
    date_parts = dates.get("date-parts") or [[]]
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    titles = item.get("title") or [""]
    containers = item.get("container-title") or []
    return {
        "title": str(titles[0]).strip(),
        "doi": normalize_doi(item.get("DOI")),
        "venue": containers[0] if containers else None,
        "year": year if isinstance(year, int) else None,
        "authors": _authors_crossref(item),
        "citations": int(item.get("is-referenced-by-count") or 0),
        "publisher_url": item.get("URL"),
        "open_access": False,
        "pdf_url": None,
        "discovery_sources": ["Crossref"],
        "evidence_status": "metadata-only",
    }


def merge_records(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for source_record in records:
        record = dict(source_record)
        record["doi"] = normalize_doi(record.get("doi"))
        key = f"doi:{record['doi']}" if record.get("doi") else f"title:{normalize_title(record.get('title'))}:{record.get('year')}"
        if not key or key.endswith(":"):
            continue
        existing = grouped.get(key)
        if existing is None:
            grouped[key] = record
            continue
        sources = set(existing.get("discovery_sources", [])) | set(record.get("discovery_sources", []))
        existing["discovery_sources"] = sorted(sources)
        if not existing.get("doi") and record.get("doi"):
            existing["doi"] = record["doi"]
        if len(record.get("authors", [])) > len(existing.get("authors", [])):
            existing["authors"] = record["authors"]
        for field in ("venue", "publisher_url", "pdf_url"):
            if not existing.get(field) and record.get(field):
                existing[field] = record[field]
        existing["citations"] = max(existing.get("citations", 0), record.get("citations", 0))
        existing["open_access"] = bool(existing.get("open_access") or record.get("open_access"))
    ranked = sorted(
        grouped.values(),
        key=lambda item: (
            venue_score(item.get("venue")),
            int(item.get("citations") or 0),
            int(item.get("year") or 0),
            normalize_title(item.get("title")),
        ),
        reverse=True,
    )
    return ranked[:limit]


def _retry_delay(error: urllib.error.HTTPError, max_delay: float) -> float:
    """Return a bounded delay for a rate-limited response."""

    header = error.headers.get("Retry-After") if error.headers else None
    try:
        requested = float(header) if header is not None else 1.0
    except (TypeError, ValueError):
        requested = 1.0
    return min(max(requested, 0.0), max_delay)


def request_json(
    base_url: str,
    params: dict[str, str],
    timeout: float,
    *,
    rate_limit_retries: int = DEFAULT_RATE_LIMIT_RETRIES,
    max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{base_url}?{query}",
        headers={"Accept": "application/json", "User-Agent": "compliant-force-robot-literature/0.1"},
    )
    attempts = 0
    while True:
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            break
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempts >= rate_limit_retries:
                raise
            time.sleep(_retry_delay(error, max_retry_delay))
            attempts += 1
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError(f"Unexpected response from {base_url}")
    return parsed


def query_openalex(
    query: str,
    limit: int,
    year_from: int | None,
    timeout: float,
    *,
    rate_limit_retries: int = DEFAULT_RATE_LIMIT_RETRIES,
    max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
) -> list[dict[str, Any]]:
    params = {"search": query, "per-page": str(limit), "mailto": ""}
    if year_from is not None:
        params["filter"] = f"from_publication_date:{year_from}-01-01"
    payload = request_json(
        "https://api.openalex.org/works",
        params,
        timeout,
        rate_limit_retries=rate_limit_retries,
        max_retry_delay=max_retry_delay,
    )
    return [from_openalex(item) for item in (payload.get("results") or []) if isinstance(item, dict)]


def query_crossref(
    query: str,
    limit: int,
    year_from: int | None,
    timeout: float,
    *,
    rate_limit_retries: int = DEFAULT_RATE_LIMIT_RETRIES,
    max_retry_delay: float = DEFAULT_MAX_RETRY_DELAY,
) -> list[dict[str, Any]]:
    params = {"query.bibliographic": query, "rows": str(limit), "select": "DOI,title,author,container-title,published-print,published-online,issued,URL,is-referenced-by-count"}
    if year_from is not None:
        params["filter"] = f"from-pub-date:{year_from}-01-01"
    payload = request_json(
        "https://api.crossref.org/works",
        params,
        timeout,
        rate_limit_retries=rate_limit_retries,
        max_retry_delay=max_retry_delay,
    )
    message = payload.get("message") or {}
    return [from_crossref(item) for item in (message.get("items") or []) if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="English or Chinese discovery query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--venue", help="Keep records whose venue contains this text")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--rate-limit-retries",
        type=int,
        default=DEFAULT_RATE_LIMIT_RETRIES,
        help="Retry HTTP 429 responses this many times (default: 1)",
    )
    parser.add_argument(
        "--max-retry-delay",
        type=float,
        default=DEFAULT_MAX_RETRY_DELAY,
        help="Cap each HTTP 429 retry delay in seconds (default: 5)",
    )
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.rate_limit_retries < 0:
        parser.error("--rate-limit-retries must be non-negative")
    if args.max_retry_delay < 0:
        parser.error("--max-retry-delay must be non-negative")

    records: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    for source, function in (("OpenAlex", query_openalex), ("Crossref", query_crossref)):
        try:
            records.extend(
                function(
                    args.query,
                    args.limit,
                    args.year_from,
                    args.timeout,
                    rate_limit_retries=args.rate_limit_retries,
                    max_retry_delay=args.max_retry_delay,
                )
            )
        except Exception as exc:  # Network failures should not erase the other source.
            errors[source] = f"{type(exc).__name__}: {exc}"
    if args.venue:
        needle = normalize_title(args.venue)
        records = [record for record in records if needle in normalize_title(record.get("venue"))]
    result = {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query": args.query,
        "filters": {"year_from": args.year_from, "venue": args.venue, "limit": args.limit},
        "sources_queried": ["OpenAlex", "Crossref"],
        "source_errors": errors,
        "result_count": min(args.limit, len(records)),
        "results": merge_records(records, args.limit),
        "evidence_boundary": "Discovery metadata only; obtain full text through publisher or authorized university portal.",
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if records or not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
