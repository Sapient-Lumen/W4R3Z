#!/usr/bin/env python3
"""Validate evidence custody/provenance registry and generated no-go reports."""
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
REG = ROOT / "artifacts" / "registries" / "evidence-custody-provenance-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "evidence_custody_provenance_pack.py"

REQUIRED_HEADER = [
    "policy_id", "evidence_family", "custody_risk", "custody_floor", "required_records",
    "reviewer_role", "release_gate", "worksheet_refs", "support_refs", "synthetic_status",
    "public_boundary", "non_claims",
]
REQUIRED_IDS = {f"ECP-{i:03d}" for i in range(1, 15)}
ALLOWED_REF_PREFIXES = {
    "DOC": "docs/", "SCRIPT": "scripts/", "TOOL": "tools/", "REG": "artifacts/registries/",
    "EXAMPLE": "artifacts/examples/", "REPORT": "artifacts/reports/", "CHECK": "artifacts/checklists/",
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
        return ["missing artifacts/registries/evidence-custody-provenance-policy.csv"]
    rows_raw = list(csv.reader(REG.open("r", encoding="utf-8", newline="")))
    if not rows_raw:
        return ["evidence-custody-provenance-policy.csv is empty"]
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    seen: set[str] = set()
    families: set[str] = set()
    for n, row in enumerate(read_csv(REG), start=2):
        pid = row.get("policy_id", "")
        if not re.fullmatch(r"ECP-\d{3}", pid):
            errors.append(f"L{n}: invalid policy_id {pid!r}")
            continue
        if pid in seen:
            errors.append(f"L{n}: duplicate policy_id {pid}")
        seen.add(pid)
        families.add(row.get("evidence_family", ""))
        for field in REQUIRED_HEADER[1:]:
            if not row.get(field):
                errors.append(f"L{n}: {pid} missing {field}")
        if not str(row.get("release_gate") or "").startswith("blocks"):
            errors.append(f"L{n}: {pid} release_gate must start with blocks")
        for field in ["worksheet_refs", "support_refs"]:
            for tok in toks(row.get(field, "")):
                m = TOKEN_RE.match(tok)
                if not m:
                    errors.append(f"L{n}: {pid} unparseable ref token {tok!r}")
                    continue
                typ = m.group("typ"); rel = m.group("path"); pref = ALLOWED_REF_PREFIXES.get(typ)
                if not pref:
                    errors.append(f"L{n}: {pid} unknown ref type {typ!r}")
                    continue
                if not rel.startswith(pref):
                    errors.append(f"L{n}: {pid} {typ} ref must start with {pref!r}: {rel!r}")
                    continue
                if not (ROOT / rel).exists():
                    errors.append(f"L{n}: {pid} missing referenced file: {rel}")
        for field in ["public_boundary", "non_claims"]:
            if "not" not in (row.get(field) or "").lower():
                errors.append(f"L{n}: {pid} {field} must include explicit non-claim language")
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required custody/provenance policy ids: " + ", ".join(missing))
    for required_family in ["capture_scope_authorization", "custody_transfer_handoff", "sealed_or_sensitive_material", "public_derivative_lineage", "chain_gap_exception_and_dissent", "custody_provenance_gate"]:
        if required_family not in families:
            errors.append(f"missing required evidence family {required_family}")
    return errors


def main() -> int:
    errors: list[str] = []
    for name in [
        "evidence-custody-provenance-matrix.json", "evidence-custody-provenance-matrix.csv",
        "evidence-custody-burndown.json", "evidence-custody-burndown.csv",
        "custody-transfer-preview-index.csv", "evidence-custody-no-go-notice.md",
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
        print("ERROR: tools/evidence_custody_provenance_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout); sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated custody/provenance JSON parse failed: {exc}", file=sys.stderr)
        return 2
    shipped_matrix = load_json(REPORTS / "evidence-custody-provenance-matrix.json")
    shipped_burndown = load_json(REPORTS / "evidence-custody-burndown.json")
    if shipped_matrix != generated.get("custody_matrix"):
        errors.append("evidence-custody-provenance-matrix.json is stale; run tools/evidence_custody_provenance_pack.py --write")
    if shipped_burndown != generated.get("custody_burndown"):
        errors.append("evidence-custody-burndown.json is stale; run tools/evidence_custody_provenance_pack.py --write")
    if shipped_matrix.get("archive_version") != VERSION:
        errors.append("custody/provenance matrix archive_version does not match VERSION")
    for flag in ["synthetic_only", "no_live_deployment_claim", "no_live_pilot_authorization", "no_chain_of_custody_certification", "no_public_records_authorization", "no_admissibility_opinion"]:
        if shipped_matrix.get(flag) is not True:
            errors.append(f"custody/provenance matrix missing {flag} boundary flag")
    if not str(shipped_matrix.get("decision") or "").startswith("NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE"):
        errors.append("custody/provenance decision must remain NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE")
    if int(shipped_matrix.get("policy_count") or 0) < 14:
        errors.append("custody/provenance policy_count unexpectedly low")
    if int(shipped_matrix.get("missing_local_custody_record_count") or 0) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("synthetic archive should mark every custody/provenance row as missing local custody record")
    if int(shipped_matrix.get("missing_support_ref_count") or 0) != 0:
        errors.append("custody/provenance matrix has missing support/template references")
    rows = read_csv(REPORTS / "evidence-custody-provenance-matrix.csv")
    if not rows or not all((r.get("non_claims") or "") for r in rows):
        errors.append("evidence-custody-provenance-matrix.csv rows must carry non_claims")
    preview_rows = read_csv(REPORTS / "custody-transfer-preview-index.csv")
    if len(preview_rows) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("custody-transfer-preview-index.csv row count must match policy_count")
    md = (REPORTS / "evidence-custody-no-go-notice.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["no-go", "custody", "provenance", "not live election evidence", "not chain-of-custody certification", "not legal advice"]:
        if phrase not in md:
            errors.append(f"evidence-custody-no-go-notice.md missing phrase {phrase!r}")
    for bad in ["certifies chain of custody", "safe to use live", "proves fraud"]:
        if bad in md:
            errors.append(f"evidence-custody-no-go-notice.md contains prohibited phrase {bad!r}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: evidence custody/provenance pack ({VERSION}, policies={shipped_matrix['policy_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
