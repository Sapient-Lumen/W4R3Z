#!/usr/bin/env python3
"""Authority-anchor minimums for special-case voter-facing surfaces."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
CONTROL_TAG = "special_case_high_risk"
MIN_OFFICIAL_IDS = 3
ANCHOR_RE = re.compile(r"\b(?:source|xref):\s*`([^`]+)`")


def numbered_doc_id(path: Path) -> int | None:
    m = re.match(r"^(\d{1,3})[-_].*\.md$", path.name)
    if not m:
        return None
    return int(m.group(1))


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

    try:
        special_doc_ids = tagged_surface_doc_ids(load_surface_registry(), CONTROL_TAG)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    sources = load_sources()
    errors: list[str] = []
    seen_docs: set[int] = set()

    for p in sorted(DOCS_DIR.glob("*.md")):
        doc_id = numbered_doc_id(p)
        if doc_id not in special_doc_ids:
            continue
        seen_docs.add(doc_id)
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
                f"{p.relative_to(ROOT)}: expected at least {MIN_OFFICIAL_IDS} distinct official authority anchors, found {len(official)}"
            )

    missing_docs = sorted(special_doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface authority minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
