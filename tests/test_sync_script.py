from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_archive_checksum_excludes_its_own_manifest() -> None:
    script = (ROOT / "scripts" / "sync-results.sh").read_text(encoding="utf-8")
    assert "find . -type f ! -name SHA256SUMS" in script
