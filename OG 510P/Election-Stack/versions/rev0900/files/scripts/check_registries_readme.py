#!/usr/bin/env python3
"""scripts/check_registries_readme.py

Release-gate drift firewall for artifacts/registries/README.md.

Rationale:
- Registries are intentionally small public surfaces.
- When a new registry is added, maintainers should not forget to document it.

This check enforces:
- every artifacts/registries/*.csv file appears in the README's "What lives here" table.

It does NOT try to enforce the exact prose, only completeness.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REG_DIR = ROOT / "artifacts" / "registries"
README = REG_DIR / "README.md"

TABLE_HEADER = "| Registry | Purpose | Drift firewall |"
TABLE_RULE = "|---|---|---|"


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def list_csv_files() -> list[str]:
    if not REG_DIR.exists():
        return []
    return sorted([p.name for p in REG_DIR.glob("*.csv") if p.is_file()])


def parse_table_registry_names(md: str) -> set[str]:
    lines = md.splitlines()

    # Locate the first "What lives here" table by its header.
    start = None
    for i, line in enumerate(lines):
        if line.strip() == TABLE_HEADER:
            start = i
            break
    if start is None:
        fail(f"missing registries table header in {README}")

    # Next non-empty line should be the table rule.
    j = start + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j >= len(lines) or lines[j].strip() != TABLE_RULE:
        fail(f"malformed registries table in {README} (expected rule line {TABLE_RULE!r})")

    # Parse subsequent rows until a blank line or non-table line.
    out: set[str] = set()
    for k in range(j + 1, len(lines)):
        line = lines[k].rstrip("\n")
        if not line.strip():
            break
        if not line.lstrip().startswith("|"):
            break
        # Extract first cell.
        parts = [p.strip() for p in line.strip().split("|")]
        # parts looks like: ['', ' `file.csv` ', ' purpose ', ' drift ', '']
        if len(parts) < 4:
            continue
        cell = parts[1]
        m = re.search(r"`([^`]+\.csv)`", cell)
        if m:
            out.add(m.group(1).strip())
    return out


def main() -> int:
    if not README.exists():
        fail("missing artifacts/registries/README.md")

    want = set(list_csv_files())
    md = README.read_text(encoding="utf-8")
    got = parse_table_registry_names(md)

    missing = sorted(want - got)
    extra = sorted(got - want)

    if missing:
        fail("registries README missing table rows for: " + ", ".join(missing))
    if extra:
        fail("registries README lists non-existent registries: " + ", ".join(extra))

    print("PASS: registries README completeness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
