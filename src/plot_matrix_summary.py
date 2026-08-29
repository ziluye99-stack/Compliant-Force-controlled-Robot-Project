"""Render a dependency-free SVG summary of a two-rate matrix run.

The renderer intentionally uses only the Python standard library so a figure
can be regenerated in the locked MuJoCo environment without adding a plotting
dependency or an external service.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


WIDTH = 1100
HEIGHT = 620
COLORS = {
    "pi_only": "#4C566A",
    "trajectory_residual": "#0072B2",
    "gain_residual": "#D55E00",
    "joint_residual": "#009E73",
}
LABELS = {
    "pi_only": "PI-only",
    "trajectory_residual": "Trajectory residual",
    "gain_residual": "Gain residual",
    "joint_residual": "Joint residual",
}


def _metric(summary: dict[str, Any], variant: str, metric: str) -> dict[str, float]:
    try:
        value = summary["variants"][variant][metric]
        return {
            "mean": float(value["mean"]),
            "low": float(value["bootstrap_95ci"][0]),
            "high": float(value["bootstrap_95ci"][1]),
        }
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ValueError(f"summary is missing variants.{variant}.{metric}") from exc


def _delta(summary: dict[str, Any], variant: str, metric: str) -> dict[str, float]:
    try:
        value = summary["paired_delta_residual_minus_pi"][variant][metric]
        return {
            "mean": float(value["mean_delta"]),
            "low": float(value["bootstrap_95ci"][0]),
            "high": float(value["bootstrap_95ci"][1]),
        }
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ValueError(f"summary is missing paired delta for {variant}.{metric}") from exc


def _text(x: float, y: float, value: str, *, size: int = 14, anchor: str = "start", weight: str = "normal") -> str:
    escaped = html.escape(value)
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial,sans-serif" font-size="{size}px" text-anchor="{anchor}" font-weight="{weight}" fill="#222">{escaped}</text>'


def _line(x1: float, y1: float, x2: float, y2: float, *, stroke: str = "#888", width: float = 1.0, dash: str | None = None) -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{width:.2f}"{extra}/>'


def _scale(value: float, low: float, high: float, start: float, end: float) -> float:
    if high <= low:
        return (start + end) / 2
    return start + (value - low) / (high - low) * (end - start)


def _panel(
    parts: list[str],
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    values: dict[str, dict[str, float]],
    ylabel: str,
    zero_line: bool = False,
) -> None:
    left, right, top, bottom = x + 76, x + width - 20, y + 50, y + height - 54
    lows = [item["low"] for item in values.values()]
    highs = [item["high"] for item in values.values()]
    if zero_line:
        low = min(min(lows), 0.0)
        high = max(max(highs), 0.0)
        pad = max((high - low) * 0.12, 0.001)
    else:
        low = min(lows)
        high = max(highs)
        pad = max((high - low) * 0.12, 0.001)
    low -= pad
    high += pad
    parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" fill="#fff" stroke="#D0D4DA"/>')
    parts.append(_text(x + 12, y + 28, title, size=17, weight="bold"))
    parts.append(_line(left, bottom, right, bottom, stroke="#444"))
    parts.append(_line(left, top, left, bottom, stroke="#444"))
    if zero_line and low < 0 < high:
        zero_y = _scale(0, low, high, bottom, top)
        parts.append(_line(left, zero_y, right, zero_y, stroke="#999", dash="5,4"))
    for tick in range(5):
        value = low + (high - low) * tick / 4
        py = _scale(value, low, high, bottom, top)
        parts.append(_line(left, py, right, py, stroke="#E7E9EC"))
        parts.append(_text(left - 10, py + 5, f"{value:.3g}", size=11, anchor="end"))
    names = list(values)
    slot = (right - left) / max(len(names), 1)
    bar_width = min(72.0, slot * 0.56)
    for index, variant in enumerate(names):
        cx = left + slot * (index + 0.5)
        item = values[variant]
        bar_y = _scale(item["mean"], low, high, bottom, top)
        baseline = _scale(0, low, high, bottom, top) if zero_line and low < 0 < high else bottom
        rect_y = min(bar_y, baseline)
        rect_h = max(abs(baseline - bar_y), 1.0)
        color = COLORS.get(variant, "#666")
        parts.append(f'<rect x="{cx - bar_width / 2:.2f}" y="{rect_y:.2f}" width="{bar_width:.2f}" height="{rect_h:.2f}" fill="{color}" opacity="0.9"/>')
        err_low = _scale(item["low"], low, high, bottom, top)
        err_high = _scale(item["high"], low, high, bottom, top)
        parts.append(_line(cx, err_low, cx, err_high, stroke="#222", width=1.6))
        parts.append(_line(cx - 7, err_low, cx + 7, err_low, stroke="#222", width=1.6))
        parts.append(_line(cx - 7, err_high, cx + 7, err_high, stroke="#222", width=1.6))
        parts.append(_text(cx, bottom + 24, LABELS.get(variant, variant), size=11, anchor="middle"))
    parts.append(_text(x + 15, y + height / 2, ylabel, size=11, anchor="middle"))


def render_summary(summary: dict[str, Any]) -> str:
    """Return an SVG string containing two metric panels."""
    variants = ["pi_only", "trajectory_residual", "gain_residual", "joint_residual"]
    available = [variant for variant in variants if variant in summary.get("variants", {})]
    if "pi_only" not in available or len(available) < 2:
        raise ValueError("summary must contain PI-only and at least one residual variant")
    rmse = {variant: _metric(summary, variant, "force_rmse_n") for variant in available}
    deltas = {
        variant: _delta(summary, variant, "force_rmse_n")
        for variant in available
        if variant != "pi_only"
    }
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    parts.append('<rect width="100%" height="100%" fill="#FAFBFC"/>')
    parts.append(_text(WIDTH / 2, 31, "Two-rate residual force-control matrix", size=22, anchor="middle", weight="bold"))
    parts.append(_text(WIDTH / 2, 53, "Bars show means; whiskers show deterministic bootstrap 95% confidence intervals", size=13, anchor="middle"))
    _panel(parts, x=32, y=72, width=500, height=480, title="Held-out true-force RMSE", values=rmse, ylabel="RMSE (N)")
    _panel(parts, x=568, y=72, width=500, height=480, title="Paired change versus PI-only", values=deltas, ylabel="Delta RMSE (N)", zero_line=True)
    parts.append(_text(WIDTH / 2, 595, "Lower is better. Negative delta favors the residual variant.", size=12, anchor="middle"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise ValueError("summary must be a JSON object")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_summary(summary), encoding="utf-8")
    print(f"Wrote SVG figure: {args.output}")


if __name__ == "__main__":
    main()
