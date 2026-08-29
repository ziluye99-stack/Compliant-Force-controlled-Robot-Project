#!/usr/bin/env python3
"""Check the platform-neutral or hardware interface YAML contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def _mapping(value: Any, name: str, issues: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(f"{name} must be a mapping")
        return {}
    return value


def validate(path: Path, hardware_ready: bool = False) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    issues: list[str] = []
    root = _mapping(data, "root", issues)
    interface = _mapping(root.get("interface"), "interface", issues)
    frames = _mapping(root.get("frames"), "frames", issues)
    timing = _mapping(root.get("timing"), "timing", issues)
    actions = _mapping(root.get("actions"), "actions", issues)
    limits = _mapping(root.get("limits"), "limits", issues)
    safety = _mapping(root.get("safety"), "safety", issues)
    parameter_map = root.get("parameter_map")

    for section, fields in {
        "interface": ("name", "status", "units", "simulator"),
        "frames": ("world", "tool", "force_measurement"),
        "timing": ("simulator_step_s", "fast_controller_hz", "policy_hz"),
        "actions": ("interface", "shape", "unit", "range", "invalid_action"),
        "limits": ("total_contact_force_n", "penetration_m"),
        "safety": ("allowed_stage", "hardware_commands_enabled"),
    }.items():
        section_data = locals()[section]
        for field in fields:
            if field not in section_data:
                issues.append(f"missing {section}.{field}")

    status = interface.get("status")
    if status not in {"platform-neutral", "hardware-candidate", "frozen"}:
        issues.append("interface.status must be platform-neutral, hardware-candidate, or frozen")
    if interface.get("units") != "SI":
        issues.append("interface.units must be SI")
    if timing.get("fast_controller_hz", 0) <= 0 or timing.get("policy_hz", 0) <= 0:
        issues.append("controller and policy rates must be positive")
    if actions.get("hardware_commands_enabled", False) or safety.get("hardware_commands_enabled") is not False:
        if safety.get("hardware_commands_enabled") is not False:
            issues.append("hardware_commands_enabled must remain false until the hardware gate is completed")
    if not isinstance(parameter_map, list) or not parameter_map:
        issues.append("parameter_map must contain at least one entry")
    else:
        for index, item in enumerate(parameter_map):
            if not isinstance(item, dict) or not item.get("parameter") or not item.get("source") or not item.get("status"):
                issues.append(f"parameter_map[{index}] needs parameter, source, and status")

    if hardware_ready:
        if status != "frozen":
            issues.append("hardware-ready validation requires interface.status=frozen")
        if safety.get("allowed_stage") != "supervised-hardware":
            issues.append("hardware-ready validation requires safety.allowed_stage=supervised-hardware")
        pending = [str(key) for key, value in limits.items() if value == "pending-platform-selection" or value == "pending-hardware-procedure"]
        if pending:
            issues.append(f"hardware-ready validation has pending limits: {', '.join(pending)}")

    return {"path": str(path), "status": status, "hardware_ready": hardware_ready, "issues": issues, "valid": not issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path("configs/platform_neutral_interface.yaml"))
    parser.add_argument("--hardware-ready", action="store_true")
    args = parser.parse_args()
    report = validate(args.path, args.hardware_ready)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
