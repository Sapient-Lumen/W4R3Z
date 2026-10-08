#!/usr/bin/env python3
"""scripts/check_unused_sources.py

Drift firewall: keep evidence/lock/external-sources.toml lean.

Fails the release if any lockfile source ID is not cited at least once via:
  `source: <id>` or `xref: <id>`

Rationale: this repository must not slowly accumulate unused external sources.
Use scripts/report_source_usage.py for a non-blocking view.

This intentionally does NOT fetch network resources.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.md_scan import iter_markdown_files

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"

CITE_RE = re.compile(r"\b(?:source|xref):\s*`?([A-Za-z0-9_]+)`?(?=$|[\s\])};:,.])")


def parse_lock_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for m in re.finditer(r'(?m)^id\s*=\s*"([^"]+)"\s*$', text):
        ids.add(m.group(1).strip())
    return ids


# NOTE: markdown scan shared in scripts/_shared/md_scan.py


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        return 2

    lock_text = LOCK.read_text(encoding="utf-8")
    lock_ids = parse_lock_ids(lock_text)

    cited: set[str] = set()
    for p in iter_markdown_files(ROOT):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in CITE_RE.finditer(content):
            cited.add(m.group(1))

    unused = sorted(lock_ids - cited)
    if unused:
        print("ERROR: unused external source IDs (remove or cite them):", file=sys.stderr)
        for sid in unused:
            print(f"  - {sid}", file=sys.stderr)
        print("Hint: run `python3 scripts/report_source_usage.py` for details.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
