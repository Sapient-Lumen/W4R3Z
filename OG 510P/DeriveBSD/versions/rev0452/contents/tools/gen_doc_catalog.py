#!/usr/bin/env python3
"""Generate a deterministic doc catalog (LLM/human navigation aid).

Outputs:
  - Markdown (stdout): docs/414-doc-catalog.md content
  - JSON (stdout with --json): docs/_generated/doc_catalog.json content

Write outputs to the repo:
  python3 tools/gen_doc_catalog.py --write

This is intentionally conservative:
  - extracts only lightweight metadata (title, Tier/Profiles/Pillars block if present)
  - avoids timestamps for deterministic output
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_MD = DOCS / "414-doc-catalog.md"
OUT_JSON = DOCS / "_generated" / "doc_catalog.json"
CHANGELOG = ROOT / "CHANGELOG.md"

TITLE_RE = re.compile(r"^#\s+(.+?)\s*$")
TIER_RE = re.compile(r"^\*\*Tier:\*\*\s*(.+?)\s*$")
PROFILES_RE = re.compile(r"^\*\*Profiles:\*\*\s*(.+?)\s*$")
PILLARS_RE = re.compile(r"^\*\*Pillars:\*\*\s*(.+?)\s*$")
DOCNUM_RE = re.compile(r"^(\d+)-")


def _top_version() -> str:
    txt = CHANGELOG.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^##\s+(\S+)\s*$", txt, re.MULTILINE)
    return m.group(1) if m else "<generated>"


@dataclass(frozen=True)
class DocRow:
    id: str
    path: str
    title: str
    tier: str
    profiles: list[str]
    pillars: list[str]
    bytes: int
    words: int


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _parse_meta(txt: str) -> tuple[str, list[str], list[str]]:
    # Search only near the top for determinism and speed.
    tier = ""
    profiles: list[str] = []
    pillars: list[str] = []
    for line in txt.splitlines()[:40]:
        line = line.rstrip()
        if not tier:
            m = TIER_RE.match(line)
            if m:
                tier = m.group(1).strip()
                continue
        if not profiles:
            m = PROFILES_RE.match(line)
            if m:
                raw = m.group(1).strip()
                profiles = [x.strip() for x in raw.split(",") if x.strip()]
                continue
        if not pillars:
            m = PILLARS_RE.match(line)
            if m:
                raw = m.group(1).strip()
                pillars = [x.strip() for x in raw.split(",") if x.strip()]
                continue
    return tier, profiles, pillars


def _parse_title(txt: str, fallback: str) -> str:
    for line in txt.splitlines()[:10]:
        m = TITLE_RE.match(line)
        if m:
            return m.group(1).strip()
    return fallback


def _doc_id_from_name(name: str) -> str:
    m = DOCNUM_RE.match(name)
    return m.group(1) if m else ""


def collect() -> list[DocRow]:
    rows: list[DocRow] = []
    for p in sorted(DOCS.glob("*.md")):
        # Avoid self-referential size drift: do not include the generated summary doc itself.
        if p.name == OUT_MD.name:
            continue
        name = p.name
        txt = _read(p)
        doc_id = _doc_id_from_name(name) or name
        title = _parse_title(txt, fallback=name)
        tier, profiles, pillars = _parse_meta(txt)
        words = len(txt.split())
        rows.append(
            DocRow(
                id=str(doc_id),
                path=f"docs/{name}",
                title=title,
                tier=tier,
                profiles=profiles,
                pillars=pillars,
                bytes=p.stat().st_size,
                words=words,
            )
        )
    # Stable ordering: numeric doc id first, then path.
    def key(r: DocRow) -> tuple[int, str]:
        try:
            return (int(r.id) if r.id.isdigit() else 10_000_000, r.path)
        except Exception:
            return (10_000_000, r.path)

    return sorted(rows, key=key)


def emit_json(rows: list[DocRow]) -> str:
    obj = {
        "format": "derivebsd.doc_catalog.v1",
        "docs": [asdict(r) for r in rows],
    }
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def _meta_rows(rows: list[DocRow]) -> list[DocRow]:
    # Meta-engineering range is currently docs >=397 with metadata required.
    out = []
    for r in rows:
        if r.id.isdigit() and int(r.id) >= 397:
            out.append(r)
    return out


def emit_md(rows: list[DocRow]) -> str:
    total = len(rows)
    with_meta = sum(1 for r in rows if r.tier or r.profiles or r.pillars)
    meta = _meta_rows(rows)

    lines: list[str] = []
    lines.append("# Doc catalog (generated)")
    lines.append("")
    lines.append("**Tier:** A (Core)  ")
    lines.append("**Profiles:** A, B, C, D  ")
    lines.append("**Pillars:** operability, reproducibility")
    lines.append("")
    lines.append(
        "This page is generated from the contents of `docs/` and is meant as a navigation aid for humans and LLMs."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total docs: **{total}**")
    lines.append(f"- Docs with Tier/Profiles/Pillars metadata detected: **{with_meta}**")
    lines.append("- Full machine-readable catalog: `docs/_generated/doc_catalog.json`")
    lines.append("")

    lines.append("## How to refresh")
    lines.append("- `python3 tools/gen_doc_catalog.py --write`")
    lines.append("- `python3 tools/check_generated_docs.py` (fails if this doc or the JSON catalog is stale)")
    lines.append("")

    lines.append("## Meta-engineering docs (>=397)")
    lines.append("These are expected to carry explicit Tier/Profiles/Pillars metadata and are the fastest way to regain project context.")
    lines.append("")
    lines.append("| Doc | Title | Tier | Profiles | Pillars |")
    lines.append("|---:|---|---|---|---|")
    for r in meta:
        prof = ", ".join(r.profiles) if r.profiles else ""
        pill = ", ".join(r.pillars) if r.pillars else ""
        lines.append(f"| {r.id} | `{r.path}` — {r.title} | {r.tier} | {prof} | {pill} |")
    lines.append("")

    lines.append("## Related tools")
    lines.append("- `tools/gen_context_pack.py` (compact state summary)")
    lines.append("- `tools/hygiene.py` (runs all lightweight checks)")
    lines.append("- `tools/check_doc_metadata.py` (enforces metadata for meta docs)")
    lines.append("")

    lines.append(f"Last updated: {_top_version()}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    ap.add_argument("--write", action="store_true", help="Write docs/414 + docs/_generated/doc_catalog.json")
    args = ap.parse_args()

    rows = collect()

    if args.json:
        s = emit_json(rows)
        if args.write:
            OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
            OUT_JSON.write_text(s, encoding="utf-8")
        print(s, end="")
        return 0

    md = emit_md(rows)
    if args.write:
        OUT_MD.write_text(md, encoding="utf-8")
        # Always write JSON alongside when --write is used.
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(emit_json(rows), encoding="utf-8")
    print(md, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
