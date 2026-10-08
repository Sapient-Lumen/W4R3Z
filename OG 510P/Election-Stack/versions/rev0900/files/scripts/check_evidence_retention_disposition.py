#!/usr/bin/env python3
"""Validate evidence retention and redaction disposition registry."""
from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts/registries/evidence-retention-disposition.csv"
REQUIRED_HEADER = ["retention_id","track","artifact_family","retention_trigger","minimum_fields_to_preserve","redaction_floor","disposition_owner","review_window","handoff_refs","non_claims"]
REQUIRED_IDS = {f"RET-{i:03d}" for i in range(1, 9)}
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
        print("ERROR: missing artifacts/registries/evidence-retention-disposition.csv", file=sys.stderr); return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: evidence-retention-disposition.csv is empty", file=sys.stderr); return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows = [{k:(v or "").strip() for k,v in r.items()} for r in csv.DictReader(f)]
    seen: set[str] = set()
    families: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        rid = row.get("retention_id", "")
        label = f"L{idx} {rid or '?'}"
        if not re.fullmatch(r"RET-\d{3}", rid):
            errors.append(f"{label}: invalid retention_id")
            continue
        if rid in seen:
            errors.append(f"{label}: duplicate retention_id")
        seen.add(rid)
        families.add(row.get("artifact_family", ""))
        if row.get("track") not in ALLOWED_TRACKS:
            errors.append(f"{label}: invalid track {row.get('track')!r}")
        for field in REQUIRED_HEADER[2:]:
            if not row.get(field):
                errors.append(f"{label}: missing {field}")
        redaction = row.get("redaction_floor", "").lower()
        if not any(word in redaction for word in ["redact", "do not", "bounded"]):
            errors.append(f"{label}: redaction_floor must include redact, do not, or bounded")
        if "preserve" not in row.get("minimum_fields_to_preserve", "").lower():
            errors.append(f"{label}: minimum_fields_to_preserve must include preserve")
        if "not" not in row.get("non_claims", "").lower():
            errors.append(f"{label}: non_claims must contain explicit not-language")
        validate_refs(row.get("handoff_refs", ""), errors, label)
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required retention ids: " + ", ".join(missing))
    if len(families) < 8:
        errors.append("retention registry must cover at least 8 artifact families")
    if errors:
        for e in errors: print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: evidence retention disposition ({len(rows)} row(s))")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
