#!/usr/bin/env python3
"""Ensure new/changed docs referenced by the newest CHANGELOG entry only mention typed artifacts that exist.

Rationale:
- Prevent 'paper receipts' drift where a doc claims a `foo.bar.receipt` exists but no schema exists.
- Keep enforcement scoped to the newest release note entry to avoid retroactive churn.

Rule:
- Parse the newest CHANGELOG section (topmost `## <version>` block).
- Collect doc paths mentioned in that section (backticked `docs/...*.md`).
- For each such doc, find backticked artifact kinds that end in one of:
    .plan .receipt .event .report .registry .diff
  (and include at least one dot, to avoid hyphenated legacy kinds).
- Require a matching schema file: `spec/<kind>.schema.json`.

Usage:
  python3 tools/check_changelog_artifact_mentions.py

Exit codes:
  0: ok
  1: at least one missing schema
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
SPEC = ROOT / "spec"

HDR_RE = re.compile(r"^##\s+(?P<ver>\S+)\s*$")
DOC_PATH_RE = re.compile(r"`(docs/[^`\s]+?\.md)`")

# Backticked artifact kind names.
ARTIFACT_KIND_RE = re.compile(
    r"`(?P<kind>[a-z0-9][a-z0-9_.-]*\.(?:plan|receipt|event|report|registry|diff))`",
    re.IGNORECASE,
)


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

    # Collect until next header.
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if HDR_RE.match(lines[j].strip()):
            end = j
            break

    return ver, "\n".join(lines[start:end])


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
    docs: list[Path] = []
    for dp in doc_paths:
        p = (ROOT / dp).resolve()
        if p.exists():
            docs.append(p)

    missing: list[str] = []
    for p in docs:
        txt = _read(p)
        for m in ARTIFACT_KIND_RE.finditer(txt):
            kind = m.group("kind")
            # Normalize to lowercase filename convention.
            schema = SPEC / f"{kind}.schema.json"
            if not schema.exists():
                missing.append(f"{p.relative_to(ROOT)}: `{kind}` has no schema at `spec/{kind}.schema.json`")

    if missing:
        print("Changelog artifact mention check FAILED.")
        print(f"Newest release: {ver}")
        print("Fix by adding the missing schema(s) or correcting the doc to reference existing typed artifacts.")
        for e in sorted(set(missing)):
            print("-", e)
        return 1

    print("Changelog artifact mention check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
