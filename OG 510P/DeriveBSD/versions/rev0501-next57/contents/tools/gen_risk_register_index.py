#!/usr/bin/env python3
"""Generate a deterministic index for the open questions + risk register.

Why:
- docs/266 is intentionally the canonical long-form document, but it is large.
- A short generated index prevents 'amnesia drift' for humans and LLMs.

Outputs:
  - Markdown (stdout): docs/415-risk-register-index.md content
  - JSON (stdout with --json): docs/_generated/risk_register.json content

Write outputs:
  python3 tools/gen_risk_register_index.py --write

Determinism:
- No timestamps.
- Only extracts stable headings and the first Risk:/See: lines per section.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "266-open-questions-and-risk-register.md"
OUT_MD = ROOT / "docs" / "415-risk-register-index.md"
OUT_JSON = ROOT / "docs" / "_generated" / "risk_register.json"
CHANGELOG = ROOT / "CHANGELOG.md"

HEAD_RE = re.compile(r"^##\s+(.+?)\s*$")
NUM_RE = re.compile(r"^(?P<num>\d+[a-z]?)\)\s*(?P<title>.+)$")
DECIDED_TAG_RE = re.compile(r"\[DECIDED\]", re.IGNORECASE)


@dataclass(frozen=True)
class RiskRow:
    id: str
    title: str
    risk: str
    see: list[str]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def _top_version() -> str:
    txt = _read(CHANGELOG)
    m = re.search(r"^##\s+(\S+)\s*$", txt, re.MULTILINE)
    return m.group(1) if m else "<generated>"


def _extract_sections(txt: str) -> list[tuple[str, list[str]]]:
    """Return list of (heading, lines_in_section)."""
    lines = txt.splitlines()
    idxs = [i for i, l in enumerate(lines) if l.startswith("## ")]
    out: list[tuple[str, list[str]]] = []
    for k, i in enumerate(idxs):
        j = idxs[k + 1] if k + 1 < len(idxs) else len(lines)
        heading = lines[i].removeprefix("## ").strip()
        out.append((heading, lines[i + 1 : j]))
    return out


def collect() -> list[RiskRow]:
    rows: list[RiskRow] = []
    for heading, body in _extract_sections(_read(SRC)):
        if DECIDED_TAG_RE.search(heading):
            continue
        m = NUM_RE.match(heading)
        if not m:
            # Keep non-numeric headings out of the index (e.g., "Rituals").
            continue
        rid = m.group("num")
        title = m.group("title").strip()

        risk = ""
        see: list[str] = []
        for line in body[:220]:
            s = line.strip()
            if not risk and s.startswith("Risk:"):
                risk = s
                continue
            if s.startswith("See:"):
                see.append(s)
        rows.append(RiskRow(id=rid, title=title, risk=risk, see=see))

    # Stable identifier ordering: numeric ids sort by integer value, and
    # suffixed ids (for inserted follow-up items such as ``62a``) stay directly
    # after their base item instead of being dropped or pushed to the end.
    def sort_key(row: RiskRow) -> tuple[int, str]:
        m = re.fullmatch(r"(\d+)([a-z]?)", row.id)
        if not m:
            return (10_000_000, row.id)
        return (int(m.group(1)), m.group(2))

    rows.sort(key=sort_key)
    return rows


def emit_json(rows: list[RiskRow]) -> str:
    obj = {
        "format": "derivebsd.risk_register.v1",
        "source": "docs/266-open-questions-and-risk-register.md",
        "items": [asdict(r) for r in rows],
    }
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def emit_md(rows: list[RiskRow]) -> str:
    lines: list[str] = []
    lines.append("# Risk register index (generated)")
    lines.append("")
    lines.append("**Tier:** A (Core)  ")
    lines.append("**Profiles:** A, B, C, D  ")
    lines.append("**Pillars:** operability")
    lines.append("")
    lines.append("This is a compact, deterministic index for the canonical long-form register: `docs/266-open-questions-and-risk-register.md`.")
    lines.append("")
    lines.append("- Machine-readable index: `docs/_generated/risk_register.json`")
    lines.append("")
    lines.append("## How to refresh")
    lines.append("- `python3 tools/gen_risk_register_index.py --write`")
    lines.append("- `python3 tools/check_generated_docs.py` (fails if this doc or the JSON index is stale)")
    lines.append("")

    lines.append("## Items")
    lines.append("| # | Topic | Risk |")
    lines.append("|---:|---|---|")
    for r in rows:
        risk = r.risk or "(missing Risk: line)"
        # Keep the risk cell short; it's an index.
        if len(risk) > 140:
            risk = risk[:137] + "…"
        lines.append(f"| {r.id} | {r.title} | {risk} |")
    lines.append("")

    lines.append("## Notes")
    lines.append("- Treat missing `Risk:` lines as a hygiene failure; each item should state the failure mode explicitly.")
    lines.append("- The index intentionally does not copy full sections; use `docs/266-...` for details and mitigation." )
    lines.append("")
    lines.append(f"Last updated: {_top_version()}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    ap.add_argument("--write", action="store_true", help="Write docs/415 + docs/_generated/risk_register.json")
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
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(emit_json(rows), encoding="utf-8")
    print(md, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
