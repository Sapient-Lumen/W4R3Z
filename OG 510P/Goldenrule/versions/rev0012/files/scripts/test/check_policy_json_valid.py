#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    files = sorted((root / "policy").glob("*.json"))
    if not files:
        print("policy-json: no policy files found", file=sys.stderr)
        return 1

    bad: list[str] = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(rel)
            continue

        if not isinstance(obj, dict):
            bad.append(rel)
            continue

        if "schema_version" in obj and not isinstance(obj["schema_version"], int):
            bad.append(rel)

    if bad:
        for b in bad:
            print(f"policy-json: invalid {b}", file=sys.stderr)
        return 1

    print(f"policy-json: ok ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
