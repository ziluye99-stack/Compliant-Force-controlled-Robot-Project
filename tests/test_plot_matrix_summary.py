import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "src" / "plot_matrix_summary.py"
SPEC = importlib.util.spec_from_file_location("plot_matrix_summary", MODULE_PATH)
assert SPEC and SPEC.loader
plotter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plotter)


def _summary() -> dict:
    metric = {
        "mean": 1.0,
        "bootstrap_95ci": [0.9, 1.1],
    }
    return {
        "variants": {
            "pi_only": {"force_rmse_n": metric},
            "joint_residual": {"force_rmse_n": {"mean": 0.8, "bootstrap_95ci": [0.7, 0.9]}},
        },
        "paired_delta_residual_minus_pi": {
            "joint_residual": {"force_rmse_n": {"mean_delta": -0.2, "bootstrap_95ci": [-0.3, -0.1]}}
        },
    }


def test_render_summary_is_valid_svg() -> None:
    svg = plotter.render_summary(_summary())
    assert svg.startswith("<svg ")
    assert "PI-only" in svg
    assert "Joint residual" in svg
    assert "delta" in svg.lower()


def test_cli_writes_summary_svg(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    output = tmp_path / "figure.svg"
    summary.write_text(json.dumps(_summary()), encoding="utf-8")
    plotter.main.__module__
    rendered = plotter.render_summary(json.loads(summary.read_text(encoding="utf-8")))
    output.write_text(rendered, encoding="utf-8")
    assert output.is_file()
    assert output.stat().st_size > 1000
