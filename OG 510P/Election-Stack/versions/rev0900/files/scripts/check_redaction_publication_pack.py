#!/usr/bin/env python3
"""Validate redaction/public-publication registry and generated no-go reports."""
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
REG = ROOT / "artifacts" / "registries" / "redaction-publication-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "redaction_publication_pack.py"

REQUIRED_HEADER = [
    "policy_id",
    "evidence_family",
    "private_data_risk",
    "public_release_floor",
    "required_redactions",
    "reviewer_role",
    "release_gate",
    "template_refs",
    "support_refs",
    "synthetic_status",
    "public_boundary",
    "non_claims",
]
REQUIRED_IDS = {f"RPP-{i:03d}" for i in range(1, 15)}
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
        return ["missing artifacts/registries/redaction-publication-policy.csv"]
    with REG.open("r", encoding="utf-8", newline="") as f:
        rows_raw = list(csv.reader(f))
    if not rows_raw:
        return ["redaction-publication-policy.csv is empty"]
    header = [h.strip() for h in rows_raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")
    seen: set[str] = set()
    families: set[str] = set()
    for n, row in enumerate(read_csv(REG), start=2):
        pid = row.get("policy_id", "")
        if not re.fullmatch(r"RPP-\d{3}", pid):
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
        for field in ["template_refs", "support_refs"]:
            for tok in toks(row.get(field, "")):
                m = TOKEN_RE.match(tok)
                if not m:
                    errors.append(f"L{n}: {pid} unparseable ref token {tok!r}")
                    continue
                typ = m.group("typ")
                rel = m.group("path")
                pref = ALLOWED_REF_PREFIXES.get(typ)
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
        errors.append("missing required redaction/publication policy ids: " + ", ".join(missing))
    for required_family in ["public_surface_parity_snapshot", "intimidation_or_safety_report", "official_ai_use_review_log", "court_packet_index", "local_pilot_intake"]:
        if required_family not in families:
            errors.append(f"missing required evidence family {required_family}")
    return errors


def main() -> int:
    errors: list[str] = []
    for name in [
        "redaction-publication-matrix.json",
        "redaction-publication-matrix.csv",
        "redaction-publication-burndown.json",
        "redaction-publication-burndown.csv",
        "public-release-preview-index.csv",
        "redaction-publication-no-go-notice.md",
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
        print("ERROR: tools/redaction_publication_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated redaction/publication JSON parse failed: {exc}", file=sys.stderr)
        return 2
    shipped_matrix = load_json(REPORTS / "redaction-publication-matrix.json")
    shipped_burndown = load_json(REPORTS / "redaction-publication-burndown.json")
    if shipped_matrix != generated.get("redaction_matrix"):
        errors.append("redaction-publication-matrix.json is stale; run tools/redaction_publication_pack.py --write")
    if shipped_burndown != generated.get("redaction_burndown"):
        errors.append("redaction-publication-burndown.json is stale; run tools/redaction_publication_pack.py --write")
    if shipped_matrix.get("archive_version") != VERSION:
        errors.append("redaction-publication-matrix archive_version does not match VERSION")
    if shipped_matrix.get("synthetic_only") is not True or shipped_matrix.get("no_live_deployment_claim") is not True:
        errors.append("redaction-publication-matrix missing synthetic/live-evidence boundary flags")
    if shipped_matrix.get("no_public_release_authorization") is not True:
        errors.append("redaction-publication-matrix missing no_public_release_authorization flag")
    if not str(shipped_matrix.get("decision") or "").startswith("NO_GO_PUBLIC_RELEASE"):
        errors.append("redaction/publication decision must remain NO_GO_PUBLIC_RELEASE")
    if int(shipped_matrix.get("policy_count") or 0) < 14:
        errors.append("redaction/publication policy_count unexpectedly low")
    if int(shipped_matrix.get("missing_local_approval_count") or 0) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("synthetic archive should mark every redaction row as missing local approval")
    if int(shipped_matrix.get("missing_support_ref_count") or 0) != 0:
        errors.append("redaction/publication matrix has missing support/template references")
    rows = read_csv(REPORTS / "redaction-publication-matrix.csv")
    if not rows or not all((r.get("non_claims") or "") for r in rows):
        errors.append("redaction-publication-matrix.csv rows must carry non_claims")
    preview_rows = read_csv(REPORTS / "public-release-preview-index.csv")
    if len(preview_rows) != int(shipped_matrix.get("policy_count") or -1):
        errors.append("public-release-preview-index.csv row count must match policy_count")
    md = (REPORTS / "redaction-publication-no-go-notice.md").read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["no-go", "redaction review", "not live election evidence", "not public-release authorization", "not legal advice"]:
        if phrase not in md:
            errors.append(f"redaction-publication-no-go-notice.md missing phrase {phrase!r}")
    for bad in ["certifies", "proves fraud", "safe to publish private data"]:
        if bad in md:
            errors.append(f"redaction-publication-no-go-notice.md contains prohibited phrase {bad!r}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: redaction/publication pack ({VERSION}, policies={shipped_matrix['policy_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
