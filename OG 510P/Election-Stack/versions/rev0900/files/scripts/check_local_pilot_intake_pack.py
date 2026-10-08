#!/usr/bin/env python3
"""Validate local-pilot intake/no-go registry and generated reports."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REG = ROOT / "artifacts" / "registries" / "local-pilot-intake-requirements.csv"
REPORTS = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "local_pilot_intake_pack.py"

REQUIRED_HEADER = [
    "requirement_id",
    "phase",
    "requirement",
    "owner_role",
    "evidence_template_refs",
    "release_support_refs",
    "synthetic_placeholder_status",
    "live_pilot_gate",
    "public_boundary",
    "non_claims",
]
REQUIRED_IDS = {f"LPI-{i:03d}" for i in range(1, 18)}
ALLOWED_REF_PREFIXES = {
    "DOC": "docs/",
    "SCRIPT": "scripts/",
    "TOOL": "tools/",
    "REG": "artifacts/registries/",
    "EXAMPLE": "artifacts/examples/",
    "REPORT": "artifacts/reports/",
    "CHECK": "artifacts/checklists/",
    "TEMPLATE": "artifacts/templates/",
}
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def toks(cell: str):
    for raw in (cell or "").split(";"):
        tok = raw.strip()
        if tok:
            yield tok


def validate_registry() -> list[str]:
    errors: list[str] = []
    if not REG.exists():
        return ["missing artifacts/registries/local-pilot-intake-requirements.csv"]
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows_raw = list(csv.reader(f))
    if not rows_raw:
        return ["local-pilot-intake-requirements.csv is empty"]
    if [h.strip() for h in rows_raw[0]] != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {[h.strip() for h in rows_raw[0]]!r} want {REQUIRED_HEADER!r}")
    seen: set[str] = set()
    for n, row in enumerate(read_csv(REG), start=2):
        rid = row.get("requirement_id", "")
        if not re.fullmatch(r"LPI-\d{3}", rid):
            errors.append(f"L{n}: invalid requirement_id {rid!r}")
            continue
        if rid in seen:
            errors.append(f"L{n}: duplicate requirement_id {rid}")
        seen.add(rid)
        for field in REQUIRED_HEADER[1:]:
            if not row.get(field):
                errors.append(f"L{n}: {rid} missing {field}")
        if not str(row.get("live_pilot_gate") or "").startswith("blocks"):
            errors.append(f"L{n}: {rid} live_pilot_gate must start with blocks")
        for field in ["evidence_template_refs", "release_support_refs"]:
            for tok in toks(row.get(field, "")):
                m = TOKEN_RE.match(tok)
                if not m:
                    errors.append(f"L{n}: {rid} unparseable ref token {tok!r}")
                    continue
                typ = m.group("typ")
                rel = m.group("path")
                pref = ALLOWED_REF_PREFIXES.get(typ)
                if not pref:
                    errors.append(f"L{n}: {rid} unknown ref type {typ!r}")
                    continue
                if not rel.startswith(pref):
                    errors.append(f"L{n}: {rid} {typ} ref must start with {pref!r}: {rel!r}")
                    continue
                if not (ROOT / rel).exists():
                    errors.append(f"L{n}: {rid} missing referenced file: {rel}")
        for field in ["public_boundary", "non_claims"]:
            if "not" not in (row.get(field) or "").lower():
                errors.append(f"L{n}: {rid} {field} must include explicit non-claim language")
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required local-pilot intake ids: " + ", ".join(missing))
    return errors


def main() -> int:
    errors: list[str] = []
    for name in [
        "local-pilot-intake-matrix.json",
        "local-pilot-intake-matrix.csv",
        "local-pilot-gap-burndown.json",
        "local-pilot-gap-burndown.csv",
        "local-pilot-no-go-notice.md",
    ]:
        if not (REPORTS / name).exists():
            errors.append(f"missing artifacts/reports/{name}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    errors += validate_registry()
    proc = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print("ERROR: tools/local_pilot_intake_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated local-pilot intake JSON parse failed: {exc}", file=sys.stderr)
        return 2
    shipped_matrix = load_json(REPORTS / "local-pilot-intake-matrix.json")
    shipped_burndown = load_json(REPORTS / "local-pilot-gap-burndown.json")
    if shipped_matrix != generated.get("intake_matrix"):
        errors.append("local-pilot-intake-matrix.json is stale; run tools/local_pilot_intake_pack.py --write")
    if shipped_burndown != generated.get("gap_burndown"):
        errors.append("local-pilot-gap-burndown.json is stale; run tools/local_pilot_intake_pack.py --write")
    if shipped_matrix.get("archive_version") != VERSION:
        errors.append("local-pilot-intake-matrix archive_version does not match VERSION")
    if shipped_matrix.get("synthetic_only") is not True or shipped_matrix.get("no_live_deployment_claim") is not True:
        errors.append("local-pilot-intake-matrix missing synthetic/live-evidence boundary flags")
    if not str(shipped_matrix.get("decision") or "").startswith("NO_GO_LIVE_PILOT"):
        errors.append("local-pilot intake decision must remain NO_GO_LIVE_PILOT")
    if int(shipped_matrix.get("requirement_count") or 0) < 15:
        errors.append("local-pilot intake requirement_count unexpectedly low")
    if int(shipped_matrix.get("missing_live_evidence_count") or 0) != int(shipped_matrix.get("requirement_count") or -1):
        errors.append("synthetic archive should mark every local-pilot intake row as missing live evidence")
    if int(shipped_matrix.get("missing_support_ref_count") or 0) != 0:
        errors.append("local-pilot intake has missing support/template references")
    rows = read_csv(REPORTS / "local-pilot-intake-matrix.csv")
    if not rows or not all((r.get("non_claims") or "") for r in rows):
        errors.append("local-pilot-intake-matrix.csv rows must carry non_claims")
    md = (REPORTS / "local-pilot-no-go-notice.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["no-go", "local configuration", "not live election evidence", "not authorization", "not legal advice"]:
        if phrase not in md:
            errors.append(f"local-pilot-no-go-notice.md missing phrase {phrase!r}")
    if "certifies" in md or "proves fraud" in md:
        errors.append("local-pilot-no-go-notice.md contains prohibited certification/fraud inference language")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: local pilot intake pack ({VERSION}, requirements={shipped_matrix['requirement_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
