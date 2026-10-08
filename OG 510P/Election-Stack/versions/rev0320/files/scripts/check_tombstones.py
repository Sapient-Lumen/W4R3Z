#!/usr/bin/env python3
"""Check tombstone markdown files.

Tombstones are non-normative aliases that preserve old references after moves/renames.
See docs/163 for the policy.

This check is intentionally small and conservative:
- identifies tombstones by their first heading containing the word "Tombstone"
- requires a pointer to at least one live target (a referenced .md path that exists)
- rejects nested structure that tends to accrete normative content (e.g., subheadings)
- keeps tombstones short (size cap)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

SIZE_CAP_BYTES = 4096  # keep aliases small and obviously non-normative

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


def _extract_candidate_targets(text: str) -> set[str]:
    out: set[str] = set()
    for m in MD_PATH_RE.finditer(text):
        out.add(m.group(1).strip())
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip().strip("<>")
        target = target.split("#", 1)[0].split("?", 1)[0].strip()
        if target.endswith(".md"):
            out.add(target)
    return out


def _exists_any(candidates: set[str], base: Path) -> bool:
    for c in sorted(candidates):
        # Resolve as relative to the tombstone file, then as repo-root relative.
        p_rel = (base / c).resolve()
        if p_rel.exists() and ROOT in p_rel.parents:
            return True
        p_root = (ROOT / c.lstrip("/")).resolve()
        if p_root.exists() and ROOT in p_root.parents:
            return True
    return False


def main() -> int:
    tombstones: list[Path] = []
    for p in DOCS.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        h = _first_heading(text)
        if h and re.search(r"\bTombstone\b", h, flags=re.IGNORECASE):
            tombstones.append(p)

    if not tombstones:
        print("PASS: no tombstone docs found")
        return 0

    failures: list[str] = []

    for p in sorted(tombstones):
        rel = p.relative_to(ROOT).as_posix()
        try:
            raw = p.read_bytes()
        except Exception as e:
            failures.append(f"{rel}: unreadable ({e})")
            continue

        if len(raw) > SIZE_CAP_BYTES:
            failures.append(f"{rel}: too large for a tombstone ({len(raw)} bytes > {SIZE_CAP_BYTES})")

        text = raw.decode("utf-8", errors="replace")

        # Discourage nesting (where normative content tends to accumulate).
        for line in text.splitlines():
            if line.startswith("##"):
                failures.append(f"{rel}: contains subheading '{line.strip()}' (tombstones must be flat)")
                break

        if not re.search(r"no\s+normative\s+content", text, flags=re.IGNORECASE):
            failures.append(f"{rel}: must include an explicit 'no normative content' notice")

        candidates = _extract_candidate_targets(text)
        if not candidates:
            failures.append(f"{rel}: no referenced .md target found (expected a pointer to canonical doc)")
        elif not _exists_any(candidates, p.parent):
            failures.append(f"{rel}: referenced target(s) not found on disk: {', '.join(sorted(candidates))}")

    if failures:
        print("FAIL: tombstone policy violations")
        for f in failures:
            print(" -", f)
        return 2

    print(f"PASS: tombstone docs OK ({len(tombstones)} checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
