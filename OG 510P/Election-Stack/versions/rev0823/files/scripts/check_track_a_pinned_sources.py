#!/usr/bin/env python3
"""scripts/check_track_a_pinned_sources.py

Drift firewall: Track A docs must not depend on unpinned external sources.

Rationale:
- Track A is the deployable core.
- If a Track A control cites an external artifact, that artifact MUST be pinned
  (sha256 in evidence/lock/external-sources.toml) so independent verifiers can
  audit what was meant, even after upstream drift/link rot.

Scope:
- Numbered docs under docs/*.md whose **Track:** header contains "A".
- Normative citations are expressed as `source: <id>` (pinned). Informative references may use `xref: <id>` (may be unpinned).

This intentionally does NOT fetch network resources.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.source_refs import citation_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"

TRACK_RE = re.compile(r"^\*\*Track:\*\*\s*(.+)$", re.IGNORECASE | re.MULTILINE)
ID_RE = re.compile(r'(?m)^id\s*=\s*"([^\"]+)"\s*$')
SHA_RE = re.compile(r'(?m)^sha256\s*=\s*"([^\"]*)"\s*$')


def is_numbered_md(name: str) -> bool:
    return re.match(r"^\d{1,3}[-_].*\.md$", name) is not None


def split_blocks(text: str) -> list[str]:
    parts = re.split(r"(?m)^\[\[source\]\]\s*$", text)
    return [p.strip() for p in parts[1:] if p.strip()]


def load_lock_sha_by_id(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for b in split_blocks(text):
        mid = ID_RE.search(b)
        msha = SHA_RE.search(b)
        if not mid:
            continue
        sid = mid.group(1).strip()
        sha = (msha.group(1).strip() if msha else "")
        out[sid] = sha
    return out


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        return 2

    lock_text = LOCK.read_text(encoding="utf-8")
    sha_by_id = load_lock_sha_by_id(lock_text)

    errors: list[str] = []

    for p in sorted(DOCS.glob("*.md")):
        if not is_numbered_md(p.name):
            continue

        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue

        m = TRACK_RE.search(txt[:4000])
        if not m:
            continue
        track = m.group(1)
        if "A" not in track:
            continue

        cited = sorted(citation_ids(txt, role="source"))
        if not cited:
            continue

        unpinned = [sid for sid in cited if sha_by_id.get(sid, "") == ""]
        if unpinned:
            errors.append(
                f"{p.relative_to(ROOT)}: Track A cites unpinned sources: "
                + ", ".join(unpinned)
            )

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
