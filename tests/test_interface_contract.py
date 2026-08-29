import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check-interface-contract.py"
SPEC = importlib.util.spec_from_file_location("check_interface_contract", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def test_platform_neutral_interface_is_valid_but_not_hardware_ready() -> None:
    path = Path(__file__).parents[1] / "configs/platform_neutral_interface.yaml"
    report = checker.validate(path)
    assert report["valid"], report
    hardware_report = checker.validate(path, hardware_ready=True)
    assert not hardware_report["valid"]
    assert any("status=frozen" in issue for issue in hardware_report["issues"])


def test_interface_requires_parameter_sources(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text("interface: {status: platform-neutral}\n", encoding="utf-8")
    report = checker.validate(path)
    assert not report["valid"]
    assert any("parameter_map" in issue for issue in report["issues"])
