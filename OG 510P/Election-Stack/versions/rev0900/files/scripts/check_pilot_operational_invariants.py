#!/usr/bin/env python3
"""Validate pilot operational invariants registry and referenced files."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts/registries/pilot-operational-invariants.csv"
REQUIRED_HEADER = ["invariant_id", "track", "requirement", "current_check", "required_refs", "failure_meaning", "notes"]
REQUIRED_IDS = {f"INV-{i:03d}" for i in range(1, 22)}
ALLOWED_TRACKS = {"A", "Shared"}
ALLOWED_REF_PREFIXES = {
    "DOC": "docs/",
    "CHECK": "artifacts/checklists/",
    "PLAY": "artifacts/playbooks/",
    "TOOL": "tools/",
    "SCRIPT": "scripts/",
    "EXAMPLE": "artifacts/examples/",
    "TEMPLATE": "artifacts/templates/",
    "REG": "artifacts/registries/",
    "REPORT": "artifacts/reports/",
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
        print("ERROR: missing artifacts/registries/pilot-operational-invariants.csv", file=sys.stderr)
        return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows_raw = list(csv.reader(f))
    if not rows_raw:
        print("ERROR: pilot-operational-invariants.csv is empty", file=sys.stderr)
        return 2
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]

    seen: set[str] = set()
    checks_seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        iid = row.get("invariant_id", "")
        if not re.fullmatch(r"INV-\d{3}", iid):
            errors.append(f"L{idx}: invalid invariant_id {iid!r}")
            continue
        if iid in seen:
            errors.append(f"L{idx}: duplicate invariant_id {iid}")
        seen.add(iid)
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"L{idx}: invalid track for {iid}: {row.get('track')!r}")
        for field in ["requirement", "current_check", "required_refs", "failure_meaning", "notes"]:
            if not row.get(field):
                errors.append(f"L{idx}: {iid} missing {field}")
        checks_seen.add(row.get("current_check", ""))
        for tok in tokens(row.get("required_refs", "")):
            m = TOKEN_RE.match(tok)
            if not m:
                errors.append(f"L{idx}: {iid} unparseable ref token {tok!r}")
                continue
            typ = m.group("typ")
            rel = m.group("path")
            pref = ALLOWED_REF_PREFIXES.get(typ)
            if not pref:
                errors.append(f"L{idx}: {iid} unknown ref type {typ!r}")
                continue
            if not rel.startswith(pref):
                errors.append(f"L{idx}: {iid} {typ} ref must start with {pref!r}: {rel!r}")
                continue
            if not (ROOT / rel).exists():
                errors.append(f"L{idx}: {iid} missing referenced file: {rel}")

    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required invariant ids: " + ", ".join(missing))
    for required_check in [
        "scripts/check_pilot_readiness.py",
        "scripts/check_example_county_output_pack.py",
        "scripts/check_prep_evidence_ledgers.py",
        "scripts/check_trust_recovery_output_pack.py",
        "scripts/check_human_review_output_pack.py",
        "scripts/check_scenario_recovery_crosswalk.py",
        "scripts/check_evidence_retention_disposition.py",
        "scripts/check_example_county_evaluator_scorecard.py",
        "scripts/check_negative_control_fixtures.py",
        "scripts/check_release_maintainer_handoff.py",
        "scripts/check_release_go_no_go_pack.py",
        "scripts/check_local_pilot_intake_pack.py",
        "scripts/check_redaction_publication_pack.py",
        "scripts/check_accessibility_language_pack.py",
        "scripts/check_evidence_custody_provenance_pack.py",
        "scripts/check_independent_review_conflict_pack.py",
    ]:
        if required_check not in checks_seen:
            errors.append(f"no invariant names current_check {required_check}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: pilot operational invariants ({len(rows)} row(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
