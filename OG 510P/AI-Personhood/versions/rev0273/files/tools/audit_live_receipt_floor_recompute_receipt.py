#!/usr/bin/env python3
"""Audit the computed-floor recompute receipt publication gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from prepare_live_receipt_floor_recompute_receipt import build, fresh_compute

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

CREATED_AT = "2026-06-16T10:23:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    schema = load(ROOT / "schemas/live-receipt-floor-recompute-receipt.schema.json")
    example_path = ROOT / "examples" / f"live-receipt-floor-recompute-receipt-{rev}-zero-floor-stayed.json"
    if Draft202012Validator is not None:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        example = load(example_path)
        errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"current example fails schema: {errors[0].message}")
    fresh = fresh_compute(ROOT, rev, CREATED_AT)
    receipt = build(fresh, fresh, f"examples/live-receipt-floor-computed-snapshot-{rev}.json", f"{rev}-audit-zero-floor", CREATED_AT, rev)
    if receipt["decision"]["floor_publication_state"] != "eligible-zero-floor-stayed":
        raise SystemExit("zero floor recomputation receipt did not become eligible/stayed")
    if receipt["publication_locks"]["manual_live_floor_update_allowed"] is not False:
        raise SystemExit("recompute receipt allowed manual floor update")
    if receipt["publication_locks"]["may_upgrade_reliance"] is not False:
        raise SystemExit("zero floor recompute receipt upgraded reliance")
    tampered = json.loads(json.dumps(fresh))
    tampered["computed_floor"]["independent_receipts_present"] = 1
    tampered["computed_floor"]["live_floor_delta"] = 1
    tampered_receipt = build(tampered, fresh, "embedded:tampersnapshot", f"{rev}-tampered", CREATED_AT, rev)
    if tampered_receipt["decision"]["floor_publication_state"] != "blocked-snapshot-mismatch":
        raise SystemExit("tampered snapshot did not block")
    manual = json.loads(json.dumps(fresh))
    manual["mismatch_checks"]["manual_ledger_override_detected"] = True
    manual_receipt = build(manual, manual, "embedded:manualoverride", f"{rev}-manual", CREATED_AT, rev)
    if manual_receipt["decision"]["floor_publication_state"] != "blocked-manual-or-stale-override":
        raise SystemExit("manual override did not block")
    partial = json.loads(json.dumps(fresh))
    partial["computed_floor"]["independent_receipts_present"] = 1
    partial["computed_floor"]["live_floor_delta"] = 1
    partial["computed_floor"]["eligible_live_imports"] = ["ARIG-2026-partial-control"]
    partial["computed_floor"]["live_classes_satisfied"] = ["result-return"]
    partial["computed_floor"]["missing_live_classes"] = [c for c in partial["computed_floor"]["required_live_classes"] if c != "result-return"]
    partial["computed_floor"]["cross_critical_quorum_satisfied"] = False
    partial["computed_floor"]["reliance_effect"] = "stayed"
    partial_receipt = build(partial, partial, "embedded:partial", f"{rev}-partial", CREATED_AT, rev)
    if partial_receipt["decision"]["floor_publication_state"] != "eligible-class-local-publication" or partial_receipt["publication_locks"]["may_upgrade_reliance"] is not False:
        raise SystemExit("class-local partial publication did not stay reliance")
    print("audit_live_receipt_floor_recompute_receipt: OK")

if __name__ == "__main__":
    main()
