#!/usr/bin/env python3
"""Validate adopter authority-capture no-go reports.

This is the practical counterpart to the rev0868 quarantine: quarantined
state/local rows must become explicit adopter capture work, not disappear into
source-maintenance prose or get promoted as live voter instruction.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
REPORTS = ROOT / "artifacts" / "reports"
TOOL = ROOT / "tools" / "adopter_authority_capture_pack.py"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_EVIDENCE = {
    "adopter_capture_id", "captured_at_utc", "captured_by_role",
    "source_url_or_official_channel_id", "byte_or_text_sha256", "responsible_office",
    "public_help_route", "jurisdiction_scope", "election_scope_or_effective_date",
    "conflict_check_status", "human_approver_role", "approved_at_utc",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def quarantined_ids() -> set[str]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    out: set[str] = set()
    for r in rows:
        tags = {str(t).strip() for t in (r.get("tags") or [])}
        sha = str(r.get("sha256") or "").strip()
        if {"jurisdiction_quarantine", "not_current_voter_instruction"} <= tags and not HEX64_RE.fullmatch(sha):
            out.add(str(r.get("id") or ""))
    return {x for x in out if x}


def main() -> int:
    errors: list[str] = []
    for name in [
        "adopter-authority-capture-matrix.json",
        "adopter-authority-capture-matrix.csv",
        "adopter-authority-capture-summary.json",
    ]:
        if not (REPORTS / name).exists():
            errors.append(f"missing artifacts/reports/{name}")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2

    proc = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print("ERROR: adopter_authority_capture_pack.py --json failed", file=sys.stderr)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return 2
    try:
        generated = json.loads(proc.stdout)
    except Exception as exc:
        print(f"ERROR: generated adopter authority-capture JSON parse failed: {exc}", file=sys.stderr)
        return 2

    shipped = load_json(REPORTS / "adopter-authority-capture-matrix.json")
    shipped_summary = load_json(REPORTS / "adopter-authority-capture-summary.json")
    if shipped != generated.get("matrix"):
        errors.append("adopter-authority-capture-matrix.json is stale; run tools/adopter_authority_capture_pack.py --write")
    if shipped_summary != generated.get("summary"):
        errors.append("adopter-authority-capture-summary.json is stale; run tools/adopter_authority_capture_pack.py --write")
    if shipped.get("archive_version") != VERSION:
        errors.append("adopter authority-capture matrix archive_version does not match VERSION")
    if shipped.get("synthetic_only") is not True or shipped.get("no_current_voter_instruction_claim") is not True:
        errors.append("adopter authority-capture matrix must carry synthetic and no-current-instruction flags")
    if not str(shipped.get("decision") or "").startswith("NO_GO_PUBLIC_GUIDANCE"):
        errors.append("adopter authority-capture decision must remain public-guidance no-go")
    if "not current voter instruction" not in str(shipped.get("boundary") or "").lower():
        errors.append("adopter authority-capture boundary must say not current voter instruction")

    want = quarantined_ids()
    rows = shipped.get("rows") or []
    got = {str(r.get("source_id") or "") for r in rows if isinstance(r, dict)}
    if got != want:
        errors.append(f"adopter capture rows do not match quarantined lockfile ids (missing={sorted(want-got)[:10]}, extra={sorted(got-want)[:10]})")
    if int(shipped.get("quarantined_source_count") or 0) != len(want):
        errors.append("quarantined_source_count does not match lockfile")
    if int(shipped.get("missing_capture_count") or -1) != len(want):
        errors.append("every quarantined row must remain missing adopter capture in this synthetic archive")
    if int(shipped.get("pin_first_candidate_count") or 0) < 1:
        errors.append("expected at least one pin-first candidate in state/local quarantine queue")

    for r in rows:
        if not isinstance(r, dict):
            errors.append("adopter capture row is not an object")
            continue
        sid = str(r.get("source_id") or "")
        if r.get("promotion_allowed") is not False:
            errors.append(f"{sid}: promotion_allowed must remain false")
        if r.get("status") != "MISSING_ADOPTER_SOURCE_CAPTURE":
            errors.append(f"{sid}: status must be MISSING_ADOPTER_SOURCE_CAPTURE")
        if r.get("public_answer_gate") != "blocks_public_guidance":
            errors.append(f"{sid}: public_answer_gate must block public guidance")
        if r.get("source_role_before_promotion") != "xref_only_example_route":
            errors.append(f"{sid}: source_role_before_promotion must be xref_only_example_route")
        if "not current voter instruction" not in str(r.get("non_claims") or "").lower():
            errors.append(f"{sid}: non_claims must include not current voter instruction")
        req = set(r.get("required_evidence") or [])
        missing_req = REQUIRED_EVIDENCE - req
        if missing_req:
            errors.append(f"{sid}: required_evidence missing {sorted(missing_req)}")

    csv_rows = load_csv(REPORTS / "adopter-authority-capture-matrix.csv")
    csv_ids = {r.get("source_id", "") for r in csv_rows}
    if csv_ids != want:
        errors.append("adopter authority-capture CSV source_id set does not match lockfile quarantine set")
    if not all((r.get("status") == "MISSING_ADOPTER_SOURCE_CAPTURE" and r.get("promotion_allowed") == "False") for r in csv_rows):
        errors.append("CSV rows must keep missing-capture status and promotion_allowed=False")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: adopter authority-capture pack ({VERSION}, quarantined_sources={len(want)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
