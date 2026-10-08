#!/usr/bin/env python3
"""scripts/check_no_forbidden_example_tlds.py

Release-gate drift firewall:

Examples in this archive are frequently copied into real systems.
Using restricted/loaded TLDs like `.gov`/`.edu` as "placeholders" (e.g. `example.gov`)
can be misread as authoritative or imply a real governance boundary.

Policy: docs/231 (placeholder domains).

This check is intentionally narrow: it only flags `example.gov` / `example.edu` / `example.mil`.
It does NOT attempt to police real external references (e.g. `cisa.gov`, `eac.gov`).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

FORBIDDEN = [
    "example.gov",
    "example.edu",
    "example.mil",
]

TEXT_EXTS = {
    ".md",
    ".py",
    ".json",
    ".csv",
    ".txt",
    ".toml",
    ".yml",
    ".yaml",
}


def is_text_file(p: Path) -> bool:
    if p.suffix.lower() in TEXT_EXTS:
        return True
    # Also treat extensionless README-like files as text.
    if p.suffix == "" and p.name.upper().startswith("README"):
        return True
    return False


def main() -> int:
    hits: list[str] = []

    for p in ROOT.rglob("*"):
        if p.resolve() == SELF:
            continue
        if p.is_dir():
            continue
        # Skip the release artifact itself if present.
        if p.name.endswith(".zip"):
            continue
        if not is_text_file(p):
            continue
        try:
            data = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lower = data.lower()
        for f in FORBIDDEN:
            if f in lower:
                hits.append(f"{p.relative_to(ROOT)}: contains {f!r}")

    if hits:
        for h in hits[:200]:
            print("ERROR:", h)
        if len(hits) > 200:
            print(f"ERROR: ... {len(hits)-200} more")
        return 2

    print("PASS: no forbidden example TLD placeholders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
