#!/usr/bin/env python3
"""Release-scoped doc stamp check: ensure docs mentioned in the newest CHANGELOG entry are stamped.

Why:
  - We use docs as stable review surfaces.
  - When a doc changes in a release, its `Last updated:` stamp should reflect that release.
  - Keep enforcement release-scoped to avoid retroactive churn.

Rule:
  - Parse the newest CHANGELOG section (topmost `## <version>` block).
  - Collect doc paths mentioned in that section (backticked `docs/...*.md`).
  - For each referenced doc (excluding generated surfaces under `docs/_generated/`):
      - require a `Last updated: <version>` line
      - require the stamped version equals the newest CHANGELOG version

Usage:
  python3 tools/check_release_last_updated.py

Exit codes:
  0: ok
  1: at least one doc missing/mismatched stamp
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"

HDR_RE = re.compile(r"^##\s+(?P<ver>\S+)\s*$")
DOC_PATH_RE = re.compile(r"`(docs/[^`\s]+?\.md)`")
LAST_UPDATED_RE = re.compile(r"^Last updated:\s*(?P<ver>\S+)\s*$", re.MULTILINE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _newest_section(txt: str) -> tuple[str, str] | None:
    lines = txt.splitlines()
    start = None
    ver = ""
    for i, ln in enumerate(lines):
        m = HDR_RE.match(ln.strip())
        if m:
            start = i
            ver = m.group("ver")
            break
    if start is None:
        return None

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if HDR_RE.match(lines[j].strip()):
            end = j
            break
    return ver, "\n".join(lines[start:end])


def _extract_last_updated(txt: str) -> str | None:
    # If multiple stamps exist, treat the last one as authoritative.
    ms = list(LAST_UPDATED_RE.finditer(txt))
    if not ms:
        return None
    return ms[-1].group("ver")


def main() -> int:
    if not CHANGELOG.exists():
        print("Missing CHANGELOG.md")
        return 1

    sec = _newest_section(_read(CHANGELOG))
    if not sec:
        print("Could not find a newest CHANGELOG section.")
        return 1

    ver, body = sec

    doc_paths = sorted({m.group(1) for m in DOC_PATH_RE.finditer(body)})
    errors: list[str] = []

    for dp in doc_paths:
        if dp.startswith("docs/_generated/"):
            continue
        p = (ROOT / dp).resolve()
        if not p.exists():
            # Discovery checks handle missing paths; keep this check focused.
            continue
        txt = _read(p)
        stamp = _extract_last_updated(txt)
        if not stamp:
            errors.append(f"{dp}: missing `Last updated: {ver}` stamp")
            continue
        if stamp != ver:
            errors.append(f"{dp}: Last updated {stamp} != newest release {ver}")

    if errors:
        print("Release Last updated stamp check FAILED.")
        print(f"Newest release: {ver}")
        print("Fix by updating the doc stamp to match the newest release entry.")
        for e in errors:
            print("-", e)
        return 1

    print("Release Last updated stamp check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
