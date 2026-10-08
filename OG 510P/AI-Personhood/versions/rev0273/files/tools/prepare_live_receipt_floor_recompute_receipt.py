#!/usr/bin/env python3
"""Prepare a live receipt floor recompute receipt.

This is the publication gate after the computed floor engine. It hashes the
current computed-floor snapshot and compares it to a fresh recomputation so a
manual total, stale rollback state, or class-local partial count cannot be
presented as a reliance upgrade.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CREATED_AT = "2026-06-18T08:27:00Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def canonical_bytes(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(data: dict) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "floor-recompute-receipt"


def fresh_compute(root: Path, rev: str, created_at: str) -> dict:
    spec = importlib.util.spec_from_file_location("compute_live_receipt_floor", root / "tools" / "compute_live_receipt_floor.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute(root=root, rev=rev, created_at=created_at)


def build(snapshot: dict, fresh_snapshot: dict, snapshot_ref: str, receipt_id: str, created_at: str, revision: str) -> dict:
    floor = snapshot.get("computed_floor", {})
    required = floor.get("required_live_classes", [])
    missing = floor.get("missing_live_classes", [])
    independent = floor.get("independent_receipts_present", 0)
    expected_quorum = independent >= len(required) and not missing and bool(required)
    expected_reliance = "ordinary-reliance" if expected_quorum else "stayed"
    input_scope = snapshot.get("input_scope", {})
    all_paths = []
    for value in input_scope.values():
        if isinstance(value, list):
            all_paths.extend(value)
    checks = {
        "snapshot_current_revision": snapshot.get("revision") == revision,
        "generated_by_floor_engine": snapshot.get("generated_by_tool") == "tools/compute_live_receipt_floor.py",
        "snapshot_matches_fresh_recompute": snapshot == fresh_snapshot,
        "late_stage_paths_present_in_scope": all(key in input_scope for key in ["import_readiness_gate_paths", "activation_record_paths", "quorum_participation_record_paths"]),
        "failed_gate_summaries_present_for_exclusions": snapshot.get("mismatch_checks", {}).get("failed_gate_public_summary_present_for_exclusions") is True,
        "no_manual_ledger_override": snapshot.get("mismatch_checks", {}).get("manual_ledger_override_detected") is False,
        "no_stale_quorum_report": snapshot.get("mismatch_checks", {}).get("stale_report_detected") is False,
        "challenge_rollback_state_replayed": bool(input_scope.get("challenge_record_paths")) or not snapshot.get("exclusion_register"),
        "cross_critical_quorum_recomputed": floor.get("cross_critical_quorum_satisfied") is expected_quorum,
        "reliance_effect_matches_quorum": floor.get("reliance_effect") == expected_reliance,
        "no_private_material_in_public_release": all(not str(p).startswith("private-vault://") and "private-vault://" not in str(p) for p in all_paths),
    }
    failed = [key for key, value in checks.items() if value is not True]
    if not checks["snapshot_current_revision"]:
        state = "blocked-no-current-snapshot"
    elif not checks["snapshot_matches_fresh_recompute"]:
        state = "blocked-snapshot-mismatch"
    elif not (checks["no_manual_ledger_override"] and checks["no_stale_quorum_report"]):
        state = "blocked-manual-or-stale-override"
    elif not checks["challenge_rollback_state_replayed"]:
        state = "blocked-rollback-or-challenge-unreplayed"
    elif failed:
        state = "blocked-snapshot-mismatch"
    elif expected_quorum:
        state = "eligible-cross-critical-reliance"
    elif independent > 0:
        state = "eligible-class-local-publication"
    else:
        state = "eligible-zero-floor-stayed"
    may_publish = state.startswith("eligible-")
    may_upgrade = state == "eligible-cross-critical-reliance"
    return {
        "recompute_receipt_id": f"LRFRR-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-floor-recompute-receipt-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_computed_snapshot_ref": snapshot_ref,
        "computed_snapshot_sha256": sha256_json(snapshot),
        "snapshot_replay_summary": {
            "snapshot_id": snapshot.get("snapshot_id", "missing-snapshot-id"),
            "independent_receipts_present": independent,
            "live_floor_delta": floor.get("live_floor_delta", 0),
            "eligible_live_imports": floor.get("eligible_live_imports", []),
            "live_classes_satisfied": floor.get("live_classes_satisfied", []),
            "missing_live_classes": missing,
            "cross_critical_quorum_satisfied": floor.get("cross_critical_quorum_satisfied", False),
            "reliance_effect": floor.get("reliance_effect", "blocked"),
        },
        "recompute_checks": checks,
        "publication_locks": {
            "may_publish_computed_floor_snapshot": may_publish,
            "manual_live_floor_update_allowed": False,
            "may_increment_live_floor_from_receipt": False,
            "may_upgrade_reliance": may_upgrade,
            "recompute_receipt_required_for_reliance_upgrade": True,
            "rollback_recheck_required": True,
        },
        "decision": {
            "floor_publication_state": state,
            "may_publish_snapshot": may_publish,
            "may_upgrade_reliance": may_upgrade,
            "live_reliance_effect": "ordinary-reliance" if may_upgrade else ("stayed" if may_publish else "blocked"),
            "reason": "Computed snapshot matched fresh engine replay and remains zero/stayed." if state == "eligible-zero-floor-stayed" else ("Computed snapshot matched fresh engine replay and may be published as class-local only." if state == "eligible-class-local-publication" else ("All required live classes survived recomputation; ordinary reliance may be considered." if may_upgrade else "Floor recomputation receipt blocked: " + "; ".join(failed))),
            "blocked_actions": ["manual live-floor total edits", "reliance upgrade from stale or mismatched computed snapshots", "ordinary reliance from class-local partial receipts", "ignoring rollback/challenge state during publication"],
            "next_actions": ["publish failed-gate summaries and keep reliance stayed" if not may_upgrade else "publish reliance update only with the recomputation receipt and full audit trail", "rerun compute_live_receipt_floor.py and this receipt after any new import, challenge, rollback, or supersession record"],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    args = parser.parse_args()
    root = ROOT
    revision = (root / "VERSION").read_text(encoding="utf-8").strip()
    snapshot_path = Path(args.snapshot)
    if not snapshot_path.is_absolute():
        snapshot_path = root / snapshot_path
    snapshot = load(snapshot_path)
    fresh = fresh_compute(root, revision, args.created_at)
    ref = snapshot_path.relative_to(root).as_posix()
    record = build(snapshot, fresh, ref, args.receipt_id, args.created_at, revision)
    out = Path(args.output_dir) / f"live-receipt-floor-recompute-receipt-{safe_slug(args.receipt_id)}.json"
    write(out, record)
    print(out)

if __name__ == "__main__":
    main()
