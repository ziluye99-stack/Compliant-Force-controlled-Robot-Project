import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "check-portal-pdfs.py"
SPEC = importlib.util.spec_from_file_location("check_portal_pdfs", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_manifest_accepts_three_pdf_headers_and_records_hashes(tmp_path: Path) -> None:
    paths = {}
    for axis in ("admittance", "impedance_hybrid", "humanoid_multicontact"):
        path = tmp_path / f"{axis}.pdf"
        path.write_bytes(b"%PDF-1.7\ncontent")
        paths[axis] = path

    manifest = checker.build_manifest(tmp_path, paths)

    assert manifest["valid"] is True
    assert set(manifest["papers"]) == set(paths)
    for record in manifest["papers"].values():
        assert record["status"] == "ok"
        assert len(record["sha256"]) == 64


def test_manifest_rejects_missing_non_pdf_and_duplicate_paths(tmp_path: Path) -> None:
    valid = tmp_path / "valid.pdf"
    valid.write_bytes(b"%PDF-1.7\ncontent")
    not_pdf = tmp_path / "notes.txt"
    not_pdf.write_text("not a PDF", encoding="utf-8")

    manifest = checker.build_manifest(
        tmp_path,
        {
            "admittance": valid,
            "impedance_hybrid": not_pdf,
            "humanoid_multicontact": valid,
        },
    )

    assert manifest["valid"] is False
    assert manifest["papers"]["impedance_hybrid"]["status"] == "not_pdf"
    assert str(valid.resolve()) in manifest["duplicate_paths"]
