#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    files = sorted((root / "schemas").glob("*.json"))
    if not files:
        print("schema-json: no schema files found", file=sys.stderr)
        return 1

    bad: list[str] = []
    for p in files:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(p.relative_to(root).as_posix())
            continue
        if not isinstance(obj, dict):
            bad.append(p.relative_to(root).as_posix())

    if bad:
        for b in bad:
            print(f"schema-json: invalid {b}", file=sys.stderr)
        return 1

    print(f"schema-json: ok ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
