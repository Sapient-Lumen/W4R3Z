#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "smoke:",
    "make test-quick",
    "upload-artifact",
    "artifacts/timing/",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / ".github" / "workflows" / "ci.yml"
    if not path.exists():
        print(f"ci-smoke: missing {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED if s not in text]
    if missing:
        for s in missing:
            print(f"ci-smoke: missing '{s}'", file=sys.stderr)
        return 1

    print(f"ci-smoke: ok ({path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
