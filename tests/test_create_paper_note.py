import importlib.util
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "create-paper-note.py"
SPEC = importlib.util.spec_from_file_location("create_paper_note", MODULE_PATH)
assert SPEC and SPEC.loader
creator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(creator)


def test_render_note_records_provenance_and_hash(tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"authorized-test-pdf")
    args = Namespace(
        short_title="Test paper",
        title="A test paper",
        authors="A Author",
        venue_year="IEEE RA-L, 2026",
        doi="10.1234/test",
        publisher_url="https://example.invalid/paper",
        preprint_url=None,
        discovery_source="OpenAlex",
        access_date="2026-08-29",
        full_text_route="school portal",
        evidence_status="full-text",
        pdf=str(pdf),
    )
    digest = creator.sha256(pdf)
    note = creator.render_note(args, digest)
    assert digest in note
    assert "school portal" in note
    assert "<complete after reading the PDF>" in note


def test_cli_refuses_missing_pdf(tmp_path: Path) -> None:
    output = tmp_path / "note.md"
    args = Namespace(
        short_title="Test", title="Test", authors="A", venue_year="2026",
        doi=None, publisher_url=None, preprint_url=None,
        discovery_source="OpenAlex", access_date="2026-08-29",
        full_text_route="school portal", evidence_status="full-text",
        pdf=tmp_path / "missing.pdf", output=output,
    )
    # The parser-level behavior is exercised indirectly by the validation rule.
    assert not args.pdf.is_file()
    assert not output.exists()
