#!/usr/bin/env python3
"""scripts/check_doc_backtick_refs.py

Drift firewall: ensure that *code-span* references to numbered docs resolve.

Why this exists:
- `scripts/check_doc_links.py` verifies markdown links, but many docs cite other docs
  as backticked filenames (e.g., `63-some-doc.md`).
- Typos in those references do not show up as broken links, but they *do* confuse
  maintainers and reviewers.

Scope (intentionally narrow to avoid false positives):
- Only checks backticked references that look like numbered docs:
    `NN-title.md` or `NNN-title.md`, optionally prefixed with `docs/`.

It does NOT attempt to validate ranges like `146–149`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

# Backticked numbered docs, optionally with a docs/ prefix.
RE_REF = re.compile(r"`(?:(docs)/)?(\d{2,3}-[a-z0-9][a-z0-9-]*\.md)`")


def iter_markdown_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*.md"):
        if not p.is_file():
            continue
        # Exclude vendored / generated outputs outside docs; keep it simple.
        # (Generated markdown inside docs is still useful to scan.)
        out.append(p)
    return sorted(out)


def line_no(text: str, idx: int) -> int:
    # 1-indexed line number
    return text.count("\n", 0, idx) + 1


def main() -> int:
    if not DOCS_DIR.exists():
        print("ERROR: missing docs/ directory", file=sys.stderr)
        return 2

    problems: list[str] = []

    for md in iter_markdown_files(ROOT):
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue

        for m in RE_REF.finditer(text):
            filename = m.group(2)
            target = DOCS_DIR / filename
            if not target.exists():
                ln = line_no(text, m.start())
                problems.append(f"{md.relative_to(ROOT)}:{ln}: missing docs/{filename}")

    if problems:
        print("FAIL: unresolved backtick doc references")
        for p in problems:
            print("  ", p)
        return 2

    print("PASS: backtick doc references resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
