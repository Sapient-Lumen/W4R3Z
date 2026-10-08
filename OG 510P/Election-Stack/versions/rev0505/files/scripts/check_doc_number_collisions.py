#!/usr/bin/env python3
"""scripts/check_doc_number_collisions.py

Fail fast if numbered doc IDs collide.

Policy:
- A doc ID is the numeric prefix in `docs/<ID>-*.md`.
- Multiple files may share an ID only if **at most one** is canonical; the rest MUST be tombstones.
  Tombstones are detected by an H1 that begins with "Tombstone".

Rationale:
- prevents silent ambiguity in citations and backtick refs
- keeps renames safe by forcing tombstone aliases instead of parallel canon docs
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

RE_NUMBERED = re.compile(r"^(?P<id>\d{2,3})-.*\.md$", re.IGNORECASE)
RE_TOMBSTONE_H1 = re.compile(r"^#\s*Tombstone\b", re.IGNORECASE)


def is_tombstone(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        return False
    # Only treat as tombstone if the *first* markdown heading is a tombstone marker.
    for line in txt.splitlines():
        if not line.strip():
            continue
        return bool(RE_TOMBSTONE_H1.match(line.strip()))
    return False


def main() -> int:
    if not DOCS.exists():
        raise SystemExit(f"docs/ directory not found at: {DOCS}")

    by_id: dict[str, list[Path]] = {}
    for p in DOCS.glob("*.md"):
        m = RE_NUMBERED.match(p.name)
        if not m:
            continue
        doc_id = m.group("id")
        by_id.setdefault(doc_id, []).append(p)

    problems: list[str] = []
    for doc_id, paths in sorted(by_id.items(), key=lambda kv: int(kv[0])):
        if len(paths) <= 1:
            continue

        tombstones = [p for p in paths if is_tombstone(p)]
        canon = [p for p in paths if p not in tombstones]

        if len(canon) == 0:
            problems.append(f"Doc ID {doc_id} has only tombstones (no canonical doc): {', '.join(p.name for p in paths)}")
        elif len(canon) > 1:
            problems.append(
                "Doc ID {id} has multiple canonical docs: {canon} (tombstones: {tombs})".format(
                    id=doc_id,
                    canon=", ".join(p.name for p in canon),
                    tombs=", ".join(p.name for p in tombstones) if tombstones else "none",
                )
            )

    if problems:
        msg = "\n".join(["Numbered doc ID collisions detected:"] + [f"- {p}" for p in problems])
        raise SystemExit(msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
