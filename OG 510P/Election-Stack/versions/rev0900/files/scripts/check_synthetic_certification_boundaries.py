#!/usr/bin/env python3
"""Validate synthetic/certification boundary registry and public outputs."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "synthetic-certification-boundaries.csv"
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
REQUIRED_HEADER = ["boundary_id", "applies_to", "required_phrase", "prohibited_inference", "checked_by", "refs", "notes"]
REQUIRED_IDS = {f"SCB-{i:03d}" for i in range(1, 6)}
ALLOWED_REF_PREFIXES = {"DOC":"docs/", "CHECK":"artifacts/checklists/", "TOOL":"tools/", "SCRIPT":"scripts/", "EXAMPLE":"artifacts/examples/", "TEMPLATE":"artifacts/templates/", "REG":"artifacts/registries/"}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def tokens(cell: str):
    for raw in (cell or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def read_json(name: str):
    return json.loads((OUTDIR / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print("ERROR: missing artifacts/registries/synthetic-certification-boundaries.csv", file=sys.stderr)
        return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: synthetic-certification-boundaries.csv is empty", file=sys.stderr)
        return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k:(v or "").strip() for k,v in r.items()} for r in csv.DictReader(f)]
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        bid = row.get("boundary_id", "")
        if not re.fullmatch(r"SCB-\d{3}", bid):
            errors.append(f"L{idx}: invalid boundary_id {bid!r}")
            continue
        if bid in seen:
            errors.append(f"L{idx}: duplicate boundary_id {bid}")
        seen.add(bid)
        for field in REQUIRED_HEADER[1:]:
            if not row.get(field):
                errors.append(f"L{idx}: {bid} missing {field}")
        if "certification" not in row.get("prohibited_inference", "").lower() and bid == "SCB-004":
            errors.append(f"L{idx}: SCB-004 must explicitly prohibit certification inference")
        for tok in tokens(row.get("refs", "")):
            m = TOKEN_RE.match(tok)
            if not m:
                errors.append(f"L{idx}: {bid} unparseable ref token {tok!r}")
                continue
            typ, rel = m.group("typ"), m.group("path")
            pref = ALLOWED_REF_PREFIXES.get(typ)
            if not pref:
                errors.append(f"L{idx}: {bid} unknown ref type {typ!r}")
                continue
            if not rel.startswith(pref):
                errors.append(f"L{idx}: {bid} {typ} ref must start with {pref!r}: {rel!r}")
                continue
            if not (ROOT / rel).exists():
                errors.append(f"L{idx}: {bid} missing referenced file: {rel}")
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required boundary ids: " + ", ".join(missing))

    # Public markdown boundary must be visibly early and explicit.
    for name in ["public-verifier-quickstart.md", "public-failure-bulletin.md", "human-review-quickstart.md", "public-evaluator-scorecard.md", "public-negative-control-summary.md"]:
        path = OUTDIR / name
        if not path.exists():
            errors.append(f"missing generated public boundary file: {path.relative_to(ROOT)}")
            continue
        head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:8]).lower()
        if "synthetic example only" not in head:
            errors.append(f"{path.relative_to(ROOT)}: missing early 'Synthetic example only' boundary")
        if "not live election evidence" not in head:
            errors.append(f"{path.relative_to(ROOT)}: missing early live-evidence non-claim")

    for name in ["scenario.json", "evidence-map.json", "trust-recovery-matrix.json", "human-review-matrix.json", "evaluator-scorecard.json", "negative-control-report.json"]:
        path = OUTDIR / name
        if not path.exists():
            errors.append(f"missing generated JSON boundary file: {path.relative_to(ROOT)}")
            continue
        try:
            obj = read_json(name)
        except Exception as e:
            errors.append(f"{path.relative_to(ROOT)}: JSON parse failed: {e}")
            continue
        if obj.get("synthetic_only") is not True:
            errors.append(f"{path.relative_to(ROOT)}: missing synthetic_only=true")
        if name in {"scenario.json", "evidence-map.json", "trust-recovery-matrix.json", "human-review-matrix.json", "evaluator-scorecard.json", "negative-control-report.json"} and obj.get("no_live_deployment_claim") is not True:
            errors.append(f"{path.relative_to(ROOT)}: missing no_live_deployment_claim=true")

    for name in ["court-packet-index.csv", "reviewer-worksheet-index.csv", "evaluator-scorecard.csv", "negative-control-results.csv"]:
        path = OUTDIR / name
        if not path.exists():
            errors.append(f"missing generated CSV boundary file: {path.relative_to(ROOT)}")
            continue
        with path.open("r", encoding="utf-8", newline="") as f:
            rows2 = list(csv.DictReader(f))
        if not rows2:
            errors.append(f"{path.relative_to(ROOT)}: empty boundary CSV")
        if not any("non_claim" in h for h in (rows2[0].keys() if rows2 else [])):
            errors.append(f"{path.relative_to(ROOT)}: no non_claim column")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: synthetic certification boundaries ({len(rows)} row(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
