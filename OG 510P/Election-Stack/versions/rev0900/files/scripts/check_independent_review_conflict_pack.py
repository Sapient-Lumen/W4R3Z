#!/usr/bin/env python3
"""Validate independent-review/conflict registry and generated no-go reports."""
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
REG = ROOT / "artifacts" / "registries" / "independent-review-conflict-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "independent_review_conflict_pack.py"

REQUIRED_HEADER = [
    "policy_id", "review_family", "review_risk", "review_floor", "required_records",
    "reviewer_role", "release_gate", "worksheet_refs", "support_refs", "synthetic_status",
    "public_boundary", "non_claims",
]
REQUIRED_IDS = {f"IRP-{i:03d}" for i in range(1, 15)}
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
        return ["missing artifacts/registries/independent-review-conflict-policy.csv"]
    rows_raw = list(csv.reader(REG.open("r", encoding="utf-8", newline="")))
    if not rows_raw:
        return ["independent-review-conflict-policy.csv is empty"]
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    seen: set[str] = set()
    families: set[str] = set()
    for n, row in enumerate(read_csv(REG), start=2):
        pid = row.get("policy_id", "")
        if not re.fullmatch(r"IRP-\d{3}", pid):
            errors.append(f"L{n}: invalid policy_id {pid!r}")
            continue
        if pid in seen:
            errors.append(f"L{n}: duplicate policy_id {pid}")
        seen.add(pid)
        families.add(row.get("review_family", ""))
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
        errors.append("missing required independent-review/conflict policy ids: " + ", ".join(missing))
    for required_family in ["reviewer_independence_scope", "conflict_of_interest_disclosure", "reproducibility_transcript", "dissent_and_minority_report", "adversarial_challenge_and_red_team_bounds", "independent_review_gate"]:
        if required_family not in families:
            errors.append(f"missing required review family {required_family}")
    return errors


def main() -> int:
    errors: list[str] = []
    for name in [
        "independent-review-matrix.json", "independent-review-matrix.csv",
        "independent-review-burndown.json", "independent-review-burndown.csv",
        "reviewer-role-preview-index.csv", "independent-review-no-go-notice.md",
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
        print("ERROR: tools/independent_review_conflict_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout); sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated independent-review/conflict JSON parse failed: {exc}", file=sys.stderr)
        return 2
    shipped_matrix = load_json(REPORTS / "independent-review-matrix.json")
    shipped_burndown = load_json(REPORTS / "independent-review-burndown.json")
    if shipped_matrix != generated.get("review_matrix"):
        errors.append("independent-review-matrix.json is stale; run tools/independent_review_conflict_pack.py --write")
    if shipped_burndown != generated.get("review_burndown"):
        errors.append("independent-review-burndown.json is stale; run tools/independent_review_conflict_pack.py --write")
    if shipped_matrix.get("archive_version") != VERSION:
        errors.append("independent-review matrix archive_version does not match VERSION")
    for flag in ["synthetic_only", "no_live_deployment_claim", "no_third_party_validation_claim", "no_certification_claim", "no_live_pilot_authorization", "no_public_release_authorization", "no_admissibility_opinion", "no_live_system_testing_authorization"]:
        if shipped_matrix.get(flag) is not True:
            errors.append(f"independent-review matrix missing {flag} boundary flag")
    if not str(shipped_matrix.get("decision") or "").startswith("NO_GO_INDEPENDENT_REVIEW_CONFLICT"):
        errors.append("independent-review/conflict decision must remain NO_GO_INDEPENDENT_REVIEW_CONFLICT")
    if int(shipped_matrix.get("policy_count") or 0) < 14:
        errors.append("independent-review/conflict policy_count unexpectedly low")
    if int(shipped_matrix.get("missing_independent_review_evidence_count") or 0) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("synthetic archive should mark every independent-review row as missing local review evidence")
    if int(shipped_matrix.get("missing_support_ref_count") or 0) != 0:
        errors.append("independent-review/conflict matrix has missing support/template references")
    rows = read_csv(REPORTS / "independent-review-matrix.csv")
    if not rows or not all((r.get("non_claims") or "") for r in rows):
        errors.append("independent-review-matrix.csv rows must carry non_claims")
    preview_rows = read_csv(REPORTS / "reviewer-role-preview-index.csv")
    if len(preview_rows) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("reviewer-role-preview-index.csv row count must match policy_count")
    md = (REPORTS / "independent-review-no-go-notice.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["no-go", "independent", "conflict", "not third-party validation", "not certification", "not legal advice"]:
        if phrase not in md:
            errors.append(f"independent-review-no-go-notice.md missing phrase {phrase!r}")
    for bad in ["certifies", "safe to use live", "proves fraud", "authorizes live testing"]:
        if bad in md:
            errors.append(f"independent-review-no-go-notice.md contains prohibited phrase {bad!r}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: independent review/conflict pack ({VERSION}, policies={shipped_matrix['policy_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
