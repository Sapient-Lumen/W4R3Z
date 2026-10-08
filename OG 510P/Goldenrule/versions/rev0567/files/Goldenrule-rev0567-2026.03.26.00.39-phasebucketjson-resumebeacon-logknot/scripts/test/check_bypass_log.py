#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "artifacts" / "security" / "bypass-log.yaml"
    if not path.exists():
        print("bypass-log: ok (no bypass log present)")
        return 0

    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for idx, ln in enumerate(lines, start=1):
        if not ln.startswith("- "):
            print(f"bypass-log: invalid line {idx}", file=sys.stderr)
            return 1
        payload = ln[2:]
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            print(f"bypass-log: invalid json at line {idx}", file=sys.stderr)
            return 1
        for k in ["timestamp_utc", "hook", "reason"]:
            if k not in obj or not str(obj[k]).strip():
                print(f"bypass-log: missing {k} at line {idx}", file=sys.stderr)
                return 1

    print(f"bypass-log: ok ({len(lines)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
