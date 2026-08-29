from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_archive_checksum_excludes_its_own_manifest() -> None:
    script = (ROOT / "scripts" / "sync-results.sh").read_text(encoding="utf-8")
    assert "find . -type f ! -name SHA256SUMS" in script


def test_archive_cli_accepts_explicit_remote_root_and_documents_precedence() -> None:
    script = (ROOT / "scripts" / "sync-results.sh").read_text(encoding="utf-8")
    workflow = (ROOT / "docs" / "workflow.md").read_text(encoding="utf-8")
    assert "--remote-artifact-root)" in script
    assert 'remote_artifact_root="${REMOTE_ARTIFACT_ROOT:-}"' in script
    assert "--remote-artifact-root <path>" in script
    assert "REMOTE_ARTIFACT_ROOT=/home/gbu/research/worktrees" in workflow
