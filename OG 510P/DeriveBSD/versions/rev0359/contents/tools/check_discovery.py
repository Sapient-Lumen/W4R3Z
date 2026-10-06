#!/usr/bin/env python3
"""Lightweight discovery-surface checks.

Purpose:
  - prevent 'amnesia drift' by ensuring critical entry points are wired
  - ensure each release bumps the 'New in <version>' section in docs/00-index.md (and that it remains the first New-in block)
  - ensure docs/00-index.md has a Last updated stamp matching the newest release
  - ensure top-level changelog mentions refer to real repo paths
  - ensure numbered docs mentioned in the newest CHANGELOG entry are discoverable

This is intentionally conservative and fast.

Usage:
  python3 tools/check_discovery.py

Exit codes:
  0: ok
  1: violations found
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHANGELOG = ROOT / "CHANGELOG.md"
INDEX = ROOT / "docs" / "00-index.md"
JUICY = ROOT / "docs" / "110-juicy-os-lessons.md"

# Repo-relative paths in backticks.
PATH_RE = re.compile(r"`((docs|rfcs|adrs|spec|tools)/[^`]+?)`")
CHANGELOG_TOP_RE = re.compile(r"^##\s+(\S+)\s*$", re.MULTILINE)
DOC_PATH_RE = re.compile(r"^docs/(?P<num>\d+)-.+\.md$")

NEW_IN_HDR_RE = re.compile(r"^##\s+New in\s+(?P<ver>\S+)\b", re.MULTILINE)
LAST_UPDATED_RE = re.compile(r"^Last updated:\s*(?P<ver>\S+)\s*$", re.MULTILINE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _top_version() -> str:
    m = CHANGELOG_TOP_RE.search(_read(CHANGELOG))
    if not m:
        raise ValueError("missing top '## <version>' entry in CHANGELOG.md")
    return m.group(1)


def _extract_changelog_top_block() -> str:
    txt = _read(CHANGELOG)
    m = CHANGELOG_TOP_RE.search(txt)
    if not m:
        return ""
    start = m.start()
    m2 = CHANGELOG_TOP_RE.search(txt, m.end())
    return txt[start : (m2.start() if m2 else len(txt))]


def _index_has_new_in(version: str) -> bool:
    pat = re.compile(rf"^##\s+New in\s+{re.escape(version)}\b", re.MULTILINE)
    return bool(pat.search(_read(INDEX)))


def _index_new_in_block(version: str) -> str:
    txt = _read(INDEX)
    hdr = re.compile(rf"^##\s+New in\s+{re.escape(version)}\b.*$", re.MULTILINE)
    m = hdr.search(txt)
    if not m:
        return ""
    start = m.start()
    # Next New-in header ends this block.
    nxt = re.compile(r"^##\s+New in\s+\S+\b", re.MULTILINE)
    m2 = nxt.search(txt, m.end())
    return txt[start : (m2.start() if m2 else len(txt))]


def _index_links_to(path: str) -> bool:
    # Keep it simple: existence of repo-relative target in the index text is enough.
    return path in _read(INDEX)



def _index_first_new_in_version() -> str | None:
    m = NEW_IN_HDR_RE.search(_read(INDEX))
    return m.group("ver") if m else None


def _index_last_updated_version() -> str | None:
    m = LAST_UPDATED_RE.search(_read(INDEX))
    return m.group("ver") if m else None



def main() -> int:
    errors: list[str] = []

    try:
        v = _top_version()
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        v = None

    if v:
        if not _index_has_new_in(v):
            errors.append(f"docs/00-index.md missing '## New in {v} ...' section")

        first = _index_first_new_in_version()
        if first and first != v:
            errors.append(
                f"docs/00-index.md newest 'New in' block should be first; found New in {first} before New in {v}"
            )

        lu = _index_last_updated_version()
        if not lu:
            errors.append("docs/00-index.md missing 'Last updated: <version>' stamp")
        elif lu != v:
            errors.append(f"docs/00-index.md Last updated stamp ({lu}) != newest CHANGELOG version ({v})")

        # Critical 'amnesia-resistor' wiring.
        must_link = [
            "docs/99-llm-runbook.md",
            "docs/420-context-pack.md",
            "docs/_generated/context_pack.json",
            "docs/411-product-profiles-as-compilation-target.md",
            "spec/examples/product.profiles.json",
            "docs/414-doc-catalog.md",
            "docs/_generated/doc_catalog.json",
            "docs/415-risk-register-index.md",
            "docs/_generated/risk_register.json",
            "docs/418-artifact-index.md",
            "docs/_generated/artifact_index.json",
        ]
        for p in must_link:
            if not _index_links_to(p):
                errors.append(f"docs/00-index.md does not mention/link {p}")

    # Changelog top entry paths must exist, and numbered docs mentioned there must be discoverable.
    block = _extract_changelog_top_block()
    mentioned = [m[0] for m in PATH_RE.findall(block)]

    for rel in mentioned:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"CHANGELOG.md references missing path: {rel}")

    # If the release mentioned numbered docs, ensure they are discoverable and included in the release notes.
    if v:
        new_in = _index_new_in_block(v)
        if not new_in:
            errors.append(f"docs/00-index.md missing 'New in {v}' block body")

        juicy_txt = _read(JUICY) if JUICY.exists() else ""
        index_txt = _read(INDEX)

        for rel in mentioned:
            m = DOC_PATH_RE.match(rel)
            if not m:
                continue

            # Only enforce wiring and release-note mention for numbered docs; that's the highest ROI amnesia surface.
            if rel not in index_txt and rel not in juicy_txt:
                errors.append(
                    f"{rel} mentioned in CHANGELOG top entry but not linked from docs/00-index.md or docs/110-juicy-os-lessons.md"
                )

            if new_in and rel not in new_in:
                errors.append(f"{rel} mentioned in CHANGELOG top entry but missing from docs/00-index.md 'New in {v}' section")

    if errors:
        print("Discovery checks failed:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Discovery checks: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
