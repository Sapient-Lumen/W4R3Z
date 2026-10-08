#!/usr/bin/env python3
"""Validate human-review handoff playbook rows and references."""
from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts/registries/human-review-handoff-playbook.csv"
REQUIRED_HEADER = ["review_id","track","review_trigger","primary_reviewer","secondary_reviewer","required_inputs","worksheet_ref","decision_outputs","escalation_condition","public_boundary_sentence","retention_action","handoff_refs","non_claims"]
REQUIRED_IDS = {f"HRH-{i:03d}" for i in range(1, 11)}
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

def validate_refs(refs: str, errors: list[str], label: str) -> None:
    for tok in tokens(refs):
        m = TOKEN_RE.match(tok)
        if not m:
            errors.append(f"{label}: unparseable ref token {tok!r}")
            continue
        typ = m.group("typ")
        rel = m.group("path")
        pref = ALLOWED_REF_PREFIXES.get(typ)
        if not pref:
            errors.append(f"{label}: unknown ref type {typ!r}")
            continue
        if not rel.startswith(pref):
            errors.append(f"{label}: {typ} ref must start with {pref!r}: {rel!r}")
            continue
        if not (ROOT / rel).exists():
            errors.append(f"{label}: missing referenced file: {rel}")


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print("ERROR: missing artifacts/registries/human-review-handoff-playbook.csv", file=sys.stderr); return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: human-review-handoff-playbook.csv is empty", file=sys.stderr); return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k:(v or "").strip() for k,v in r.items()} for r in csv.DictReader(f)]
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        rid = row.get("review_id", "")
        label = f"L{idx} {rid or '?'}"
        if not re.fullmatch(r"HRH-\d{3}", rid):
            errors.append(f"{label}: invalid review_id")
            continue
        if rid in seen:
            errors.append(f"{label}: duplicate review_id")
        seen.add(rid)
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"{label}: invalid track {row.get('track')!r}")
        for field in REQUIRED_HEADER[2:]:
            if not row.get(field):
                errors.append(f"{label}: missing {field}")
        worksheet = row.get("worksheet_ref", "")
        if worksheet and not (ROOT / worksheet).exists():
            errors.append(f"{label}: missing worksheet_ref {worksheet}")
        sentence = row.get("public_boundary_sentence", "")
        if sentence and not sentence.endswith("."):
            errors.append(f"{label}: public_boundary_sentence must end with a period")
        low_sentence = sentence.lower()
        for hedge in BANNED_PUBLIC_HEDGES:
            if hedge in low_sentence:
                errors.append(f"{label}: public_boundary_sentence contains banned hedge {hedge!r}")
        nc = row.get("non_claims", "").lower()
        for phrase in ["not", "outcome"]:
            if phrase not in nc:
                errors.append(f"{label}: non_claims must contain {phrase!r}")
        if "preserve" not in row.get("retention_action", "").lower():
            errors.append(f"{label}: retention_action must include preserve")
        validate_refs(row.get("handoff_refs", ""), errors, label)
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required human-review ids: " + ", ".join(missing))
    if len(rows) < 10:
        errors.append("human-review handoff playbook must cover at least 10 review modes")
    if errors:
        for e in errors: print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: human-review handoff playbook ({len(rows)} row(s))")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
