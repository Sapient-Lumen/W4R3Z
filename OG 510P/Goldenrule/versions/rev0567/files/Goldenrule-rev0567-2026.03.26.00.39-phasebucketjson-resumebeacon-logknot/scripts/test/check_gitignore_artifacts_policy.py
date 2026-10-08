#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_SNIPPETS = [
    "/artifacts/*",
    "!/artifacts/.gitkeep",
    "!/artifacts/timing/.gitkeep",
    "!/artifacts/security/.gitkeep",
    "!/artifacts/process/.gitkeep",
    "!/artifacts/release/.gitkeep",
    "!/artifacts/formal/.gitkeep",
    "!/artifacts/reports/.gitkeep",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    text = (root / ".gitignore").read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SNIPPETS if s not in text]
    if missing:
        for s in missing:
            print(f"gitignore-policy: missing '{s}'", file=sys.stderr)
        return 1

    print(f"gitignore-policy: ok ({len(REQUIRED_SNIPPETS)} rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
