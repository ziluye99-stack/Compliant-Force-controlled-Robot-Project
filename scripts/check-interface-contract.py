#!/usr/bin/env python3
"""Check the platform-neutral or hardware interface YAML contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.interface_contract import validate


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
