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


def test_focused_branch_requires_explicit_vision_read_marker(tmp_path: Path) -> None:
    task_dir = tmp_path / "docs" / "tasks"
    task_dir.mkdir(parents=True)
    (task_dir / "example.md").write_text(
        "# Task\n\n- docs/PROJECT_VISION.md\n- Stage gate: simulation\n"
        "- Expected artifact: test\n\n## Verification\n\nrun\n"
        "- Project priority: reproducibility\n- Branch: `codex/example`\n",
        encoding="utf-8",
    )
    report = checker.validate_branch_task(tmp_path, "codex/example")
    assert not report["valid"]
    assert "task brief missing marker: Read `docs/PROJECT_VISION.md`" in report["issues"]


def test_focused_branch_requires_checked_vision_gate(tmp_path: Path) -> None:
    task_dir = tmp_path / "docs" / "tasks"
    task_dir.mkdir(parents=True)
    (task_dir / "example.md").write_text(
        "# Task\n\nRead `docs/PROJECT_VISION.md` before branch work.\n"
        "- Stage gate: simulation\n- Expected artifact: test\n\n"
        "## Verification\n\nrun\n- Project priority: reproducibility\n"
        "- Branch: `codex/example`\n- [ ] `docs/PROJECT_VISION.md` was read\n",
        encoding="utf-8",
    )
    report = checker.validate_branch_task(tmp_path, "codex/example")
    assert not report["valid"]
    assert "task brief must check the docs/PROJECT_VISION.md gate before branch work" in report["issues"]
