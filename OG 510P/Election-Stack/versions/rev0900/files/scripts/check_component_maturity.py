#!/usr/bin/env python3
"""Drift firewall for component maturity labels.

The archive deliberately mixes deployable Track A surfaces, research support, and
speculative material.  This check keeps those lanes explicit so a Track A claim
cannot silently depend on a research/speculative component.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "component-maturity.csv"

REQUIRED_HEADER = ["component_id", "track", "maturity", "evidence_claim_allowed", "refs", "notes"]
ALLOWED_TRACKS = {"A", "B", "C", "Shared"}
ALLOWED_MATURITY = {"operational", "pilot_ready", "research", "speculative", "deprecated", "quarantined"}
ALLOWED_YN = {"yes", "no"}
CLAIM_ALLOWED_MATURITY = {"operational", "pilot_ready"}

ALLOWED_REF_PREFIXES = {
    "DOC": "docs/",
    "ADR": "adr/",
    "SCHEMA": "schemas/",
    "CHECK": "artifacts/checklists/",
    "PLAY": "artifacts/playbooks/",
    "TOOL": "tools/",
    "SCRIPT": "scripts/",
    "EXAMPLE": "artifacts/examples/",
    "TEMPLATE": "artifacts/templates/",
    "REG": "artifacts/registries/",
}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def iter_tokens(field: str):
    for raw in (field or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print(f"ERROR: missing {REG.relative_to(ROOT)}")
        return 2

    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        print("ERROR: component-maturity.csv is empty")
        return 2
    header = [c.strip() for c in rows[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r}, want {REQUIRED_HEADER!r}")

    seen: set[str] = set()
    maturities_seen: set[str] = set()
    with REG.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            cid = (row.get("component_id") or "").strip()
            track = (row.get("track") or "").strip()
            maturity = (row.get("maturity") or "").strip()
            claim = (row.get("evidence_claim_allowed") or "").strip()
            refs = (row.get("refs") or "").strip()
            notes = (row.get("notes") or "").strip()

            if not cid:
                errors.append(f"L{line_no}: missing component_id")
                continue
            if cid in seen:
                errors.append(f"L{line_no}: duplicate component_id {cid}")
            seen.add(cid)

            if track not in ALLOWED_TRACKS:
                errors.append(f"L{line_no}: invalid track for {cid}: {track!r}")
            if maturity not in ALLOWED_MATURITY:
                errors.append(f"L{line_no}: invalid maturity for {cid}: {maturity!r}")
            else:
                maturities_seen.add(maturity)
            if claim not in ALLOWED_YN:
                errors.append(f"L{line_no}: invalid evidence_claim_allowed for {cid}: {claim!r}")

            if claim == "yes" and maturity not in CLAIM_ALLOWED_MATURITY:
                errors.append(
                    f"L{line_no}: {cid} allows evidence claims while maturity={maturity}; "
                    "only operational/pilot_ready components may do that"
                )
            if maturity in {"research", "speculative", "deprecated", "quarantined"} and claim != "no":
                errors.append(f"L{line_no}: {cid} maturity={maturity} must set evidence_claim_allowed=no")
            if track == "A" and maturity == "speculative":
                errors.append(f"L{line_no}: Track A component {cid} cannot be speculative; demote track or maturity")

            if not notes:
                errors.append(f"L{line_no}: {cid} missing notes")
            if not refs:
                errors.append(f"L{line_no}: {cid} missing refs")
            for tok in iter_tokens(refs):
                m = TOKEN_RE.match(tok)
                if not m:
                    errors.append(f"L{line_no}: {cid} unparseable ref token {tok!r}")
                    continue
                typ = m.group("typ")
                pth = m.group("path")
                prefix = ALLOWED_REF_PREFIXES.get(typ)
                if not prefix:
                    errors.append(f"L{line_no}: {cid} unknown ref type {typ!r}")
                    continue
                if not pth.startswith(prefix):
                    errors.append(f"L{line_no}: {cid} {typ} ref must start with {prefix!r}: {pth!r}")
                    continue
                if not (ROOT / pth).exists():
                    errors.append(f"L{line_no}: {cid} missing referenced file: {pth}")

    # Keep at least one explicit non-deployable lane in the registry so the label set
    # does not collapse into a blanket "pilot_ready" badge.
    if "research" not in maturities_seen:
        errors.append("component-maturity.csv must include at least one research component")
    if "speculative" not in maturities_seen:
        errors.append("component-maturity.csv must include at least one speculative component")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    print(f"PASS: component maturity registry ({len(seen)} component(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
