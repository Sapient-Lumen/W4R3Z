#!/usr/bin/env python3
"""Check lock-backed official anchor coverage for promoted voter-facing family-tail docs."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
UPPER_BAND_START = 335
MIN_OFFICIAL_IDS = 2
ANCHOR_RE = re.compile(r"\b(?:source|xref):\s*`([^`]+)`")


def load_sources() -> dict[str, dict]:
    data = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    entries: list[dict] = []
    if "id" in data:
        entries.append({k: v for k, v in data.items() if k != "source"})
    entries.extend(data.get("source", []))
    out: dict[str, dict] = {}
    for e in entries:
        sid = e.get("id")
        if sid:
            out[str(sid)] = e
    return out


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}")
        return 2

    table = load_surface_registry()
    sources = load_sources()
    rows: list[tuple[int, str]] = []
    for row in table.rows:
        if not any(row.values()):
            continue
        doc_id = int(row["doc_id"])
        if doc_id < UPPER_BAND_START:
            continue
        rows.append((doc_id, row["doc_path"]))

    errors: list[str] = []
    for doc_id, rel in rows:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"missing voter-facing family-tail doc {doc_id}: {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        ids = sorted(set(ANCHOR_RE.findall(text)))
        missing = [sid for sid in ids if sid not in sources]
        official = [
            sid for sid in ids
            if "official_websites" in sources.get(sid, {}).get("tags", [])
        ]
        if missing:
            errors.append(
                f"{p.relative_to(ROOT)}: missing lockfile source IDs: {', '.join(missing)}"
            )
        if len(official) < MIN_OFFICIAL_IDS:
            errors.append(
                f"{p.relative_to(ROOT)}: expected at least {MIN_OFFICIAL_IDS} distinct official lock-backed anchors, found {len(official)}"
            )

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print(
        "PASS: voter-facing family-tail lock-backed official anchors "
        f"(docs {rows[0][0]}–{rows[-1][0]} each have >= {MIN_OFFICIAL_IDS} official xrefs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
