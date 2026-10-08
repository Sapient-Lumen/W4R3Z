#!/usr/bin/env python3
"""Validate the evaluator scoring rubric registry."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "evaluator-scoring-rubric.csv"
REQUIRED_HEADER = ["metric_id", "track", "dimension", "measurement_source", "max_points", "pass_threshold", "checked_by", "required_refs", "failure_meaning", "non_claims"]
REQUIRED_IDS = {f"ESR-{i:03d}" for i in range(1, 12)}
ALLOWED_TRACKS = {"A", "Shared"}
ALLOWED_REF_PREFIXES = {
    "DOC": "docs/",
    "CHECK": "artifacts/checklists/",
    "TOOL": "tools/",
    "SCRIPT": "scripts/",
    "EXAMPLE": "artifacts/examples/",
    "TEMPLATE": "artifacts/templates/",
    "REG": "artifacts/registries/",
}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def tokens(cell: str):
    for raw in (cell or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print("ERROR: missing artifacts/registries/evaluator-scoring-rubric.csv", file=sys.stderr)
        return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: evaluator-scoring-rubric.csv is empty", file=sys.stderr)
        return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
    seen: set[str] = set()
    total_points = 0
    for idx, row in enumerate(rows, start=2):
        mid = row.get("metric_id", "")
        if not re.fullmatch(r"ESR-\d{3}", mid):
            errors.append(f"L{idx}: invalid metric_id {mid!r}")
            continue
        if mid in seen:
            errors.append(f"L{idx}: duplicate metric_id {mid}")
        seen.add(mid)
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"L{idx}: {mid} invalid track {row.get('track')!r}")
        for field in ["dimension", "measurement_source", "checked_by", "required_refs", "failure_meaning", "non_claims"]:
            if not row.get(field):
                errors.append(f"L{idx}: {mid} missing {field}")
        try:
            max_points = int(row.get("max_points", ""))
            threshold = int(row.get("pass_threshold", ""))
        except ValueError:
            errors.append(f"L{idx}: {mid} max_points/pass_threshold must be integers")
            continue
        if max_points <= 0 or threshold <= 0 or threshold > max_points:
            errors.append(f"L{idx}: {mid} invalid point threshold {threshold}/{max_points}")
        total_points += max_points
        if "not" not in row.get("non_claims", "").lower():
            errors.append(f"L{idx}: {mid} non_claims must contain an explicit not-claim")
        for tok in tokens(row.get("required_refs", "")):
            m = TOKEN_RE.match(tok)
            if not m:
                errors.append(f"L{idx}: {mid} unparseable ref token {tok!r}")
                continue
            typ = m.group("typ")
            rel = m.group("path")
            pref = ALLOWED_REF_PREFIXES.get(typ)
            if not pref:
                errors.append(f"L{idx}: {mid} unknown ref type {typ!r}")
                continue
            if not rel.startswith(pref):
                errors.append(f"L{idx}: {mid} {typ} ref must start with {pref!r}: {rel!r}")
                continue
            if not (ROOT / rel).exists():
                errors.append(f"L{idx}: {mid} missing referenced file: {rel}")
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required metric ids: " + ", ".join(missing))
    if total_points != 100:
        errors.append(f"rubric max_points must sum to 100, got {total_points}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: evaluator scoring rubric ({len(rows)} metric(s), {total_points} points)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
