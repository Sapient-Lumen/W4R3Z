#!/usr/bin/env python3
"""Validate the trust-recovery playbook registry.

Failure handoff language is part of the evidence boundary: a verifier failure,
missing artifact, source-staleness alert, or key-change event must produce a
bounded preservation action and a safe public sentence instead of improvisation.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "trust-recovery-playbook.csv"
REQUIRED_HEADER = ["recovery_id", "track", "trigger", "minimum_evidence", "decision_owner", "public_status", "public_sentence", "operator_action", "handoff_refs", "non_claims"]
REQUIRED_IDS = {f"TRP-{i:03d}" for i in range(1, 12)}
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
}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")
BANNED_PUBLIC_HEDGES = {"maybe", "might", "possibly", "probably", "we believe", "appears to prove"}


def tokens(cell: str):
    for raw in (cell or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print("ERROR: missing artifacts/registries/trust-recovery-playbook.csv", file=sys.stderr)
        return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows_raw = list(csv.reader(f))
    if not rows_raw:
        print("ERROR: trust-recovery-playbook.csv is empty", file=sys.stderr)
        return 2
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]

    seen: set[str] = set()
    statuses: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        rid = row.get("recovery_id", "")
        if not re.fullmatch(r"TRP-\d{3}", rid):
            errors.append(f"L{idx}: invalid recovery_id {rid!r}")
            continue
        if rid in seen:
            errors.append(f"L{idx}: duplicate recovery_id {rid}")
        seen.add(rid)
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"L{idx}: invalid track for {rid}: {row.get('track')!r}")
        for field in REQUIRED_HEADER[2:]:
            if not row.get(field):
                errors.append(f"L{idx}: {rid} missing {field}")
        status = row.get("public_status", "")
        if status in statuses:
            errors.append(f"L{idx}: duplicate public_status {status}")
        statuses.add(status)
        sentence = row.get("public_sentence", "")
        if not sentence.endswith("."):
            errors.append(f"L{idx}: {rid} public_sentence must end with a period")
        low_sentence = sentence.lower()
        for hedge in BANNED_PUBLIC_HEDGES:
            if hedge in low_sentence:
                errors.append(f"L{idx}: {rid} public_sentence contains banned hedge {hedge!r}")
        nc = row.get("non_claims", "").lower()
        if "not" not in nc:
            errors.append(f"L{idx}: {rid} non_claims must contain explicit non-claim language")
        for tok in tokens(row.get("handoff_refs", "")):
            m = TOKEN_RE.match(tok)
            if not m:
                errors.append(f"L{idx}: {rid} unparseable handoff ref {tok!r}")
                continue
            typ = m.group("typ")
            rel = m.group("path")
            pref = ALLOWED_REF_PREFIXES.get(typ)
            if not pref:
                errors.append(f"L{idx}: {rid} unknown handoff ref type {typ!r}")
                continue
            if not rel.startswith(pref):
                errors.append(f"L{idx}: {rid} {typ} ref must start with {pref!r}: {rel!r}")
                continue
            if not (ROOT / rel).exists():
                errors.append(f"L{idx}: {rid} missing referenced file: {rel}")

    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required recovery ids: " + ", ".join(missing))
    if len(rows) < 10:
        errors.append("trust-recovery playbook must cover at least 10 failure modes")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: trust-recovery playbook ({len(rows)} row(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
