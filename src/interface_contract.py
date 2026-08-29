"""Load and validate the platform-neutral system interface contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _mapping(value: Any, name: str, issues: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(f"{name} must be a mapping")
        return {}
    return value


def validate(path: Path, hardware_ready: bool = False) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": str(path), "status": None, "hardware_ready": hardware_ready, "issues": [f"cannot read YAML: {exc}"], "valid": False}
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
        "interface": ("name", "version", "status", "units", "simulator"),
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
    if not isinstance(interface.get("version"), int) or interface.get("version") < 1:
        issues.append("interface.version must be a positive integer")
    if timing.get("fast_controller_hz", 0) <= 0 or timing.get("policy_hz", 0) <= 0:
        issues.append("controller and policy rates must be positive")
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
        pending = [str(key) for key, value in limits.items() if value in {"pending-platform-selection", "pending-hardware-procedure", "pending"}]
        if pending:
            issues.append(f"hardware-ready validation has pending limits: {', '.join(pending)}")

    return {"path": str(path), "status": status, "hardware_ready": hardware_ready, "issues": issues, "valid": not issues}


def load_summary(path: Path, *, hardware_ready: bool = False) -> dict[str, Any]:
    """Validate a contract and return the fields needed in a run manifest."""
    report = validate(path, hardware_ready=hardware_ready)
    if not report["valid"]:
        raise ValueError(f"invalid interface contract {path}: {'; '.join(report['issues'])}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "name": data["interface"]["name"],
        "version": data["interface"]["version"],
        "status": data["interface"]["status"],
        "simulator": data["interface"]["simulator"],
        "units": data["interface"]["units"],
        "timing": {
            "simulator_step_s": data["timing"]["simulator_step_s"],
            "fast_controller_hz": data["timing"]["fast_controller_hz"],
            "policy_hz": data["timing"]["policy_hz"],
            "action_hold_steps": data["timing"].get("action_hold_steps"),
        },
        "actions": {
            "interface": data["actions"]["interface"],
            "unit": data["actions"]["unit"],
            "range": data["actions"]["range"],
            "invalid_action": data["actions"]["invalid_action"],
        },
        "safety": {
            "hardware_commands_enabled": data["safety"]["hardware_commands_enabled"],
            "allowed_stage": data["safety"]["allowed_stage"],
            "penetration_limit_m": data["limits"]["penetration_m"],
            "total_contact_force_limit_n": data["limits"]["total_contact_force_n"],
        },
    }
