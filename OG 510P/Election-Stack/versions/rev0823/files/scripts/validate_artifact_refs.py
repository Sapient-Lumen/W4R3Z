#!/usr/bin/env python3
"""Validate artifact references in claim/evidence and hazard registers.

This script enforces the conventions in docs/163-artifact-reference-conventions.md:
TYPE:path tokens separated by semicolons.

It checks:
- token parses
- path exists
- DOC paths live under docs/
- SCHEMA paths live under schemas/
- CHECK paths live under artifacts/checklists/
- PLAY paths live under artifacts/playbooks/
- ADR paths live under adr/
"""
from pathlib import Path
import csv
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

ALLOWED = {
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

def check_csv(path: Path, columns: list[str]) -> list[str]:
    errors = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # header is line 1
            for col in columns:
                for tok in iter_tokens(row.get(col, "")):
                    m = TOKEN_RE.match(tok)
                    if not m:
                        errors.append(f"{path}:L{i}:{col}: unparseable token: {tok!r}")
                        continue
                    typ = m.group("typ")
                    pth = m.group("path")
                    if typ not in ALLOWED:
                        errors.append(f"{path}:L{i}:{col}: unknown TYPE {typ!r} in token {tok!r}")
                        continue
                    prefix = ALLOWED[typ]
                    if not pth.startswith(prefix):
                        errors.append(f"{path}:L{i}:{col}: {typ} path must start with {prefix!r}: got {pth!r}")
                        continue
                    full = ROOT / pth
                    if not full.exists():
                        errors.append(f"{path}:L{i}:{col}: missing referenced file: {pth!r}")
    return errors

def main() -> int:
    errs = []
    errs += check_csv(ROOT / "artifacts" / "claims" / "claim-evidence-matrix.csv", ["EvidenceArtifacts"])
    errs += check_csv(ROOT / "artifacts" / "hazards" / "hazard-register.csv", ["DetectionArtifacts", "ResponsePlaybook"])

    if errs:
        print("ERROR: artifact reference validation failed:", file=sys.stderr)
        for e in errs:
            print("  " + e, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
