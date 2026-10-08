#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "make doctor",
    "make test-quick",
    "make test-full",
    "make gate",
    "make gate-strict",
    "make test-formal-smoke",
    "make test-formal-tools",
    "make test-examples-json",
    "make test-doc-links",
    "make test-claim-register",
    "make test-claim-register-summary",
    "make test-risk-register",
    "make test-risk-register-summary",
    "make update-experiment-catalog",
    "make test-experiment-catalog",
    "make report-artifact-summary",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    text = (root / "README.md").read_text(encoding="utf-8")

    missing = [cmd for cmd in REQUIRED if cmd not in text]
    if missing:
        for m in missing:
            print(f"readme-commands: missing '{m}'", file=sys.stderr)
        return 1

    print(f"readme-commands: ok ({len(REQUIRED)} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
