#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    report_dir = root / "artifacts" / "reports"
    if not report_dir.exists():
        print("reports-json: ok (no reports dir)")
        return 0

    files = sorted(report_dir.glob("*.json"))
    bad: list[str] = []
    for p in files:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(p.relative_to(root).as_posix())

    if bad:
        for b in bad:
            print(f"reports-json: invalid {b}", file=sys.stderr)
        return 1

    print(f"reports-json: ok ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
