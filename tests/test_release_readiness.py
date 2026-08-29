import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check-release-readiness.py"
SPEC = importlib.util.spec_from_file_location("check_release_readiness", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


ROOT = Path(__file__).parents[1]


def test_release_contract_is_present() -> None:
    report = module.validate_release_contract(ROOT)
    assert report["valid"], report["issues"]


def test_release_checklist_does_not_claim_hardware_readiness() -> None:
    text = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
    assert "sim-to-real and" in text
    assert "human must mark each item" in text
