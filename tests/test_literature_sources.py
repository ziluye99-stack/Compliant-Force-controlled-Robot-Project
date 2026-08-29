import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "check-literature-sources.py"
SPEC = importlib.util.spec_from_file_location("check_literature_sources", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_project_source_policy_is_valid() -> None:
    report = checker.validate_policy(ROOT / "configs" / "literature_sources.yaml")
    assert report["valid"], report["issues"]


def test_policy_rejects_missing_primary_source(tmp_path: Path) -> None:
    policy = (ROOT / "configs" / "literature_sources.yaml").read_text(encoding="utf-8")
    policy = policy.replace("  - id: nature_science\n", "", 1)
    path = tmp_path / "sources.yaml"
    path.write_text(policy, encoding="utf-8")
    report = checker.validate_policy(path)
    assert not report["valid"]
    assert "missing primary source: nature_science" in report["issues"]
