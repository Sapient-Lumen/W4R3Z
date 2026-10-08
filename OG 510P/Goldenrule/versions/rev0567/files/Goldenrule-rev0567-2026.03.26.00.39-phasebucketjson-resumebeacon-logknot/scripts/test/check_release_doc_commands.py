#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "make gate",
    "make gate-strict",
    "make release-manifest RELEASE_VERSION=<version>",
    "make test-release-manifest-schema",
    "make test-release-checksums RELEASE_VERSION=<version>",
    "make test-release-hygiene RELEASE_VERSION=<version>",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    text = (root / "docs" / "RELEASE_PROCESS.md").read_text(encoding="utf-8")
    missing = [s for s in REQUIRED if s not in text]
    if missing:
        for s in missing:
            print(f"release-doc: missing '{s}'", file=sys.stderr)
        return 1

    print(f"release-doc: ok ({len(REQUIRED)} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
