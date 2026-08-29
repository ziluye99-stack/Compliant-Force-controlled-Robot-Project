import importlib.util
import io
import json
from pathlib import Path
from urllib.error import HTTPError


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "literature-query.py"
SPEC = importlib.util.spec_from_file_location("literature_query", MODULE_PATH)
assert SPEC and SPEC.loader
literature_query = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(literature_query)


def test_normalize_doi_handles_urls_and_punctuation() -> None:
    assert literature_query.normalize_doi("https://doi.org/10.1109/LRA.2020.3010739.") == "10.1109/lra.2020.3010739"


def test_merge_records_deduplicates_doi_and_preserves_sources() -> None:
    records = [
        {"title": "A force paper", "doi": "10.1/ABC", "venue": "IEEE RA-L", "year": 2024, "authors": ["A"], "citations": 2, "publisher_url": None, "open_access": False, "pdf_url": None, "discovery_sources": ["OpenAlex"], "evidence_status": "metadata-only"},
        {"title": "A force paper", "doi": "https://doi.org/10.1/abc", "venue": "IEEE RA-L", "year": 2024, "authors": ["A", "B"], "citations": 3, "publisher_url": "https://doi.org/10.1/abc", "open_access": True, "pdf_url": None, "discovery_sources": ["Crossref"], "evidence_status": "metadata-only"},
    ]
    merged = literature_query.merge_records(records, limit=10)
    assert len(merged) == 1
    assert merged[0]["discovery_sources"] == ["Crossref", "OpenAlex"]
    assert merged[0]["doi"] == "10.1/abc"
    assert merged[0]["open_access"] is True


def test_venue_priority_ranks_robotics_top_venues() -> None:
    assert literature_query.venue_score("IEEE Transactions on Robotics") > literature_query.venue_score("Unknown Journal")


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self._payload


def test_request_json_retries_rate_limit_once(monkeypatch) -> None:
    calls = []
    sleeps = []
    error = HTTPError(
        "https://example.test",
        429,
        "Too Many Requests",
        {"Retry-After": "12"},
        io.BytesIO(),
    )

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, timeout))
        if len(calls) == 1:
            raise error
        return _Response({"ok": True})

    monkeypatch.setattr(literature_query.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(literature_query.time, "sleep", sleeps.append)

    result = literature_query.request_json(
        "https://example.test/works",
        {"query": "force control"},
        2.0,
        rate_limit_retries=1,
        max_retry_delay=5.0,
    )

    assert result == {"ok": True}
    assert len(calls) == 2
    assert sleeps == [5.0]


def test_request_json_preserves_rate_limit_after_retry_budget(monkeypatch) -> None:
    error = HTTPError(
        "https://example.test",
        429,
        "Too Many Requests",
        {"Retry-After": "1"},
        io.BytesIO(),
    )
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(1)
        raise error

    monkeypatch.setattr(literature_query.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(literature_query.time, "sleep", lambda _: None)

    try:
        literature_query.request_json(
            "https://example.test/works",
            {},
            2.0,
            rate_limit_retries=1,
        )
    except HTTPError as raised:
        assert raised.code == 429
    else:
        raise AssertionError("rate-limit error should remain visible")
    assert len(calls) == 2


def test_request_json_can_disable_rate_limit_retry(monkeypatch) -> None:
    error = HTTPError(
        "https://example.test",
        429,
        "Too Many Requests",
        {},
        io.BytesIO(),
    )
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(1)
        raise error

    monkeypatch.setattr(literature_query.urllib.request, "urlopen", fake_urlopen)

    try:
        literature_query.request_json(
            "https://example.test/works",
            {},
            2.0,
            rate_limit_retries=0,
        )
    except HTTPError as raised:
        assert raised.code == 429
    else:
        raise AssertionError("rate-limit error should remain visible")
    assert len(calls) == 1
