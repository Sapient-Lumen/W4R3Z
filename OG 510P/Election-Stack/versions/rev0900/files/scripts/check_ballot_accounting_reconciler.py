#!/usr/bin/env python3
"""Release-gate the synthetic ballot-accounting reconciliation seam.

The CDF replay lane is useful only if replayed totals are not detached from
ballot accounting.  This check requires the Example County synthetic fixture to
ship an executable reconciliation report and fail closed on count, undervote, and
unknown-unit drift while preserving non-live/non-custody boundaries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ballot_accounting_reconciler as accounting_replay  # noqa: E402
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "ballot_accounting_reconciler.py"
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
BD = CDF_DIR / "ballot-definition-minimal.json"
CVR = CDF_DIR / "cast-vote-records-minimal.json"
ACCOUNTING = CDF_DIR / "ballot-accounting-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"ballot-accounting-reconciliation-rev{REV}.json"
PUBLIC = CDF_DIR / "public-ballot-accounting-reconciliation.md"
VECTORS = ROOT / "artifacts" / "test-vectors" / "ballot-accounting"
REQUIRED = [TOOL, BD, CVR, ACCOUNTING, REPORT, PUBLIC]
PASS_DECISION = "SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool(*, accounting: Path = ACCOUNTING) -> tuple[int, dict[str, Any], str]:
    """Run the reconciler in-process inside the release-gate child."""

    obj = accounting_replay.build_report(BD, CVR, accounting)
    code = 0 if obj.get("decision") == PASS_DECISION else 2
    return code, obj, ""


def require_negative(label: str, vector: Path, want_prefix: str, errors: list[str]) -> None:
    code, obj, stderr = run_tool(accounting=vector)
    if code == 0:
        errors.append(f"{label}: negative control exited 0")
    if obj.get("decision") != "FAIL_BALLOT_ACCOUNTING_RECONCILIATION":
        errors.append(f"{label}: decision {obj.get('decision')!r} != FAIL_BALLOT_ACCOUNTING_RECONCILIATION")
    problems = [str(e) for e in obj.get("errors") or []]
    if not any(p.startswith(want_prefix) for p in problems):
        errors.append(f"{label}: missing problem prefix {want_prefix!r}; got {problems!r}; stderr={stderr!r}")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2

    code, generated, stderr = run_tool()
    if code != 0:
        errors.append(f"default ballot-accounting reconciliation failed rc={code}: {stderr}")
    shipped = load_json(REPORT)
    if shipped != generated:
        errors.append("ballot-accounting reconciliation report is stale; run tools/ballot_accounting_reconciler.py --write")
    if shipped.get("archive_version") != VERSION:
        errors.append("ballot-accounting reconciliation archive_version mismatch")
    if shipped.get("decision") != PASS_DECISION:
        errors.append("ballot-accounting reconciliation must pass only as synthetic non-custody evidence")
    if shipped.get("synthetic_only") is not True or shipped.get("no_live_deployment_claim") is not True or shipped.get("no_live_custody_claim") is not True:
        errors.append("ballot-accounting reconciliation missing synthetic/no-live/no-custody flags")
    if shipped.get("no_full_nist_conformance_claim") is not True or shipped.get("no_outcome_proof_claim") is not True:
        errors.append("ballot-accounting reconciliation missing no-conformance/no-outcome-proof flags")
    counts = shipped.get("counts") or {}
    if counts.get("reporting_unit_count") != 2 or counts.get("contest_accounting_row_count") != 4 or counts.get("cvr_record_count") != 6:
        errors.append(f"unexpected ballot-accounting fixture counts: {counts!r}")
    if counts.get("error_count") != 0 or counts.get("matched_reconciliation_row_count") != counts.get("contest_accounting_row_count"):
        errors.append("default ballot-accounting reconciliation must have zero errors and all rows matched")

    public = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["not live custody evidence", "not a full nist cdf conformance result", "not the nist cdf test method", "not certification", "not outcome proof", "not current voter instruction", "not legal advice", "does not authorize live pilot use"]:
        if phrase not in public:
            errors.append(f"public ballot-accounting summary missing boundary phrase {phrase!r}")
    for bad in ["full nist cdf conformance pass", "certifies", "proves the outcome", "authorizes live pilot"]:
        if bad in public:
            errors.append(f"public ballot-accounting summary contains prohibited overclaim {bad!r}")

    require_negative("cvr-count-mismatch", VECTORS / "ballot-accounting-cvr-count-mismatch.json", "ACCOUNTING_FIELD_MISMATCH:", errors)
    require_negative("undervote-mismatch", VECTORS / "ballot-accounting-undervote-mismatch.json", "ACCOUNTING_FIELD_MISMATCH:", errors)
    require_negative("unknown-unit", VECTORS / "ballot-accounting-unknown-unit.json", "ACCOUNTING_UNKNOWN_REPORTING_UNIT:", errors)

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2
    print(f"PASS: ballot accounting reconciliation ({VERSION}, rows={counts.get('contest_accounting_row_count')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
