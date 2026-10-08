#!/usr/bin/env python3
"""scripts/check_no_tombstone_refs.py

Drift firewall: prevent normative docs from citing tombstone aliases.

Tombstones exist only to preserve *old* references after renames/moves.
They are intentionally non-normative, small, and should not become the
target of new citations.

Policy: docs/163 (artifact reference conventions).

This check:
- discovers tombstones under docs/ by first heading containing "Tombstone"
- extracts a best-effort canonical target from the tombstone body
- scans markdown surfaces (docs/ + artifacts/ + root READMEs) for references
  to tombstone filenames, excluding the tombstones themselves and the
  generated tombstone index.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARTIFACTS = ROOT / "artifacts"

MD_PATH_RE = re.compile(r"`([^`]+?\.md)`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s
        return None
    return None


def _extract_md_targets(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for m in MD_PATH_RE.finditer(text):
        t = m.group(1).strip()
        if t.endswith(".md") and t not in seen:
            out.append(t)
            seen.add(t)
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip().strip("<>")
        target = target.split("#", 1)[0].split("?", 1)[0].strip()
        if target.endswith(".md") and target not in seen:
            out.append(target)
            seen.add(target)
    return out


def _canonical_for_tombstone(tombstone_path: Path, text: str) -> str:
    """Best-effort canonical target path (under docs/ when possible)."""
    targets = _extract_md_targets(text)
    for t in targets:
        t_norm = t
        if t_norm.startswith("docs/"):
            t_norm = t_norm[len("docs/") :]

        # Prefer docs/ targets.
        cand = (DOCS / t_norm).resolve()
        if cand.exists() and ROOT in cand.parents:
            return f"docs/{cand.relative_to(DOCS).as_posix()}"

        # Allow relative-to-tombstone references.
        rel = (tombstone_path.parent / t).resolve()
        if rel.exists() and ROOT in rel.parents and DOCS in rel.parents:
            return f"docs/{rel.relative_to(DOCS).as_posix()}"
    return ""


def _discover_tombstones() -> dict[str, str]:
    """Return map: tombstone filename -> canonical docs/<file>.md (best effort)."""
    out: dict[str, str] = {}
    if not DOCS.exists():
        return out
    for p in DOCS.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        h = _first_heading(text)
        if not h or not re.search(r"\bTombstone\b", h, flags=re.IGNORECASE):
            continue
        canon = _canonical_for_tombstone(p, text)
        out[p.name] = canon
    return out


def _scan_paths() -> list[Path]:
    """Markdown surfaces to scan for tombstone references."""
    paths: list[Path] = []
    for base in [DOCS, ARTIFACTS]:
        if base.exists():
            paths.extend(sorted([p for p in base.rglob("*.md") if p.is_file()]))
    # Root readmes may also cite docs.
    for name in ["README.md", "ARCHIVE_INDEX.md"]:
        p = ROOT / name
        if p.exists():
            paths.append(p)
    return paths


def main() -> int:
    tombstones = _discover_tombstones()
    if not tombstones:
        print("PASS: no tombstones found")
        return 0

    # Exclusions: tombstones themselves, generated index, and changelog (historical references are OK).
    exclude: set[Path] = set()
    for name in tombstones.keys():
        exclude.add(DOCS / name)
    exclude.add(DOCS / "TOMBSTONES.md")
    exclude.add(ROOT / "CHANGELOG.md")

    failures: list[str] = []
    scan = _scan_paths()

    for p in scan:
        if p in exclude:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = p.relative_to(ROOT).as_posix()

        for i, line in enumerate(text.splitlines(), start=1):
            for tomb_name, canonical in tombstones.items():
                if tomb_name not in line:
                    continue

                hint = f"use {canonical}" if canonical else "use the canonical target"
                failures.append(f"{rel}:{i}: cites tombstone '{tomb_name}' ({hint})")

    if failures:
        print("FAIL: tombstone references found (cite canonical docs instead)")
        for f in failures[:80]:
            print(" -", f)
        if len(failures) > 80:
            print(f" ... ({len(failures) - 80} more)")
        return 2

    print("PASS: no tombstone references in normative markdown surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
