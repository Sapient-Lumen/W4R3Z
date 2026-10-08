#!/usr/bin/env python3
"""scripts/check_adr_index.py

Drift firewall for ADRs.

Validates:
- every ADR file under adr/ (excluding INDEX.md) has:
  - a header like "# ADR 0002: Title"
  - a Status and Date line in the standard bullet form
- adr/INDEX.md lists every ADR number in its table

This is intentionally lightweight and stdlib-only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "adr"
INDEX = ADR_DIR / "INDEX.md"

RE_ADR_FILE = re.compile(r"^(\d{4})-.*\.md$")
RE_HEADER = re.compile(r"^#\s*ADR\s+(\d{4})\s*[:—\-]\s*(.+?)\s*$")
RE_STATUS = re.compile(r"^\s*-\s*Status:\s*\*\*(.+?)\*\*\s*$")
RE_DATE = re.compile(r"^\s*-\s*Date:\s*\*\*(\d{4}-\d{2}-\d{2})\*\*\s*$")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)


def main() -> int:
    if not ADR_DIR.exists():
        fail("missing adr/ directory")
        return 2
    if not INDEX.exists():
        fail("missing adr/INDEX.md")
        return 2

    index_text = INDEX.read_text(encoding="utf-8")

    any_fail = False
    adr_files = sorted(p for p in ADR_DIR.glob("*.md") if p.name != "INDEX.md")

    if not adr_files:
        # ADRs are optional, but if the directory exists, we expect at least the bootstrap ADR.
        fail("no ADR files found under adr/")
        return 2

    for p in adr_files:
        m = RE_ADR_FILE.match(p.name)
        if not m:
            fail(f"adr filename must start with 4 digits: {p.name}")
            any_fail = True
            continue

        expected_num = m.group(1)
        lines = p.read_text(encoding="utf-8").splitlines()
        header = next((ln for ln in lines if ln.strip().startswith("#")), "")
        mh = RE_HEADER.match(header.strip())
        if not mh:
            fail(f"{p}: missing or malformed ADR header (expected '# ADR {expected_num}: <title>')")
            any_fail = True
        else:
            num = mh.group(1)
            if num != expected_num:
                fail(f"{p}: header ADR number {num} does not match filename {expected_num}")
                any_fail = True

        has_status = any(RE_STATUS.match(ln) for ln in lines)
        has_date = any(RE_DATE.match(ln) for ln in lines)
        if not has_status:
            fail(f"{p}: missing '- Status: **...**' line")
            any_fail = True
        if not has_date:
            fail(f"{p}: missing '- Date: **YYYY-MM-DD**' line")
            any_fail = True

        if f"| {expected_num} |" not in index_text:
            fail(f"adr/INDEX.md missing table row for ADR {expected_num}")
            any_fail = True

    if any_fail:
        return 2

    print("OK ADR index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
