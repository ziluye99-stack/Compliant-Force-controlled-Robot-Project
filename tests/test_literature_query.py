import importlib.util
from pathlib import Path


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
