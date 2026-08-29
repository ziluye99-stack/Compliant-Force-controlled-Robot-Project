import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "check-branch-task.py"
SPEC = importlib.util.spec_from_file_location("check_branch_task", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_current_branch_has_a_task_brief() -> None:
    report = checker.validate_branch_task(ROOT, "codex/dual-contact-mujoco")
    assert report["valid"], report["issues"]


def test_main_is_allowed_without_a_task_brief() -> None:
    report = checker.validate_branch_task(ROOT, "main")
    assert report["valid"]


def test_focused_branch_requires_matching_task_file() -> None:
    report = checker.validate_branch_task(ROOT, "codex/not-yet-defined")
    assert not report["valid"]
    assert "missing task brief" in report["issues"][0]
