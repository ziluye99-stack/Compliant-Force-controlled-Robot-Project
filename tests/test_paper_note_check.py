import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check-paper-notes.py"
SPEC = importlib.util.spec_from_file_location("check_paper_notes", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_existing_full_text_notes_have_required_evidence() -> None:
    archive = Path("/mnt/research-data")
    if not archive.is_mount():
        pytest.skip("research archive is not mounted; PDF verification runs where the archive is available")
    notes = sorted((Path(__file__).parents[1] / "docs/literature/notes").glob("*.md"))
    reports = [checker.validate_note(path, require_full_text=True, verify_files=True) for path in notes]
    assert reports
    assert all(report["valid"] for report in reports), reports
    assert all(report["full_text_file_status"] == "verified" for report in reports)


def test_metadata_only_note_is_rejected_at_full_text_gate(tmp_path: Path) -> None:
    note = tmp_path / "candidate.md"
    note.write_text(
        """# Candidate\n\n## Bibliographic record\n\n- Title: Candidate\n- Authors: A\n- Venue and year: Journal, 2024\n- DOI: 10.1/example\n- Discovery source and access date: OpenAlex, 2026-08-29\n- Full-text access route (publisher, school portal, repository, or preprint): metadata record\n- Evidence status (`full-text`, `accepted-manuscript`, `preprint`, or `metadata-only`): metadata-only\n\n## Translation and terminology\n\nTranslation pending.\n\n## Technical digest\n\nDigest pending.\n\n## Experimental design analysis\n\nAnalysis pending.\n\n## Assessment\n\nAssessment pending.\n\n## Follow-up experiment in MuJoCo\n\nFollow-up pending.\n""",
        encoding="utf-8",
    )
    report = checker.validate_note(note, require_full_text=True)
    assert not report["valid"]
    assert "full-text evidence is required for this gate" in report["issues"]
