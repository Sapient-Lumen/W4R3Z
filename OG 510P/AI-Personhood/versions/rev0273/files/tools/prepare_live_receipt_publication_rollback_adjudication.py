#!/usr/bin/env python3
"""Prepare a live receipt publication rollback adjudication record.

This is the gate after a floor recompute receipt. It proves that publication or
continued reliance posture has replayed late challenges, rollback duties,
revocations, and supersession state. It never increments the live floor.
"""
from __future__ import annotations

import argparse
import hashlib
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
    return re.sub(r"[^A-Za-z0-9._:-]+", "-", value.strip()).strip("-") or "publication-rollback-adjudication"


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _challenge_open_or_uncompleted(challenge: dict) -> bool:
    state = challenge.get("challenge_state")
    decision = challenge.get("decision", {})
    if state in {"pre-import-challenge", "post-import-challenge", "rollback-required"}:
        return decision.get("rollback_completed") is not True
    return False


def _upheld_without_completed_rollback(challenge: dict) -> bool:
    decision = challenge.get("decision", {})
    if decision.get("challenge_upheld") is not True:
        return False
    return not (decision.get("rollback_required") is True and decision.get("rollback_completed") is True and decision.get("live_floor_change_allowed") is False)


def _challenge_summary_ready(challenge: dict) -> bool:
    return bool(challenge.get("public_summary_ref")) and challenge.get("recheck_matrix", {}).get("failed_gate_public_summary_updated") is True


def build(*, recompute_receipt: dict, recompute_receipt_ref: str, snapshot: dict | None, snapshot_ref: str, snapshot_hash: str, challenges: list[dict], challenge_refs: list[str], receipt_id: str, created_at: str, revision: str, simulate_supersession_open: bool = False, signal_ingresses: list[dict] | None = None, signal_refs: list[str] | None = None, remedy_resolutions: list[dict] | None = None, remedy_resolution_refs: list[str] | None = None, remedy_executions: list[dict] | None = None, remedy_execution_refs: list[str] | None = None) -> dict:
    summary = recompute_receipt.get("snapshot_replay_summary", {})
    decision = recompute_receipt.get("decision", {})
    locks = recompute_receipt.get("publication_locks", {})
    checks = recompute_receipt.get("recompute_checks", {})
    snapshot_hash_matches = bool(snapshot) and recompute_receipt.get("computed_snapshot_sha256") == snapshot_hash
    late_change_refs = list(challenge_refs)
    open_challenges = [c.get("challenge_record_id", "unknown") for c in challenges if _challenge_open_or_uncompleted(c)]
    uncompleted_rollbacks = [c.get("challenge_record_id", "unknown") for c in challenges if _upheld_without_completed_rollback(c)]
    challenge_summaries_ready = all(_challenge_summary_ready(c) for c in challenges) if challenges else True
    signal_ingresses = signal_ingresses or []
    signal_refs = signal_refs or []
    unresolved_signal_states = {
        "opened-publication-rollback-required",
        "blocked-unretained-signal",
        "blocked-private-material-in-public-ingress",
        "blocked-supersession-unrouted",
        "blocked-unknown-source",
    }
    unresolved_signal_ingresses = [
        s.get("late_change_ingress_id", "unknown")
        for s in signal_ingresses
        if s.get("decision", {}).get("late_change_state") in unresolved_signal_states
    ]
    signal_ingress_replayed = all(
        s.get("no_direct_floor_effect") is True
        and s.get("publication_freeze_locks", {}).get("may_increment_live_floor_from_ingress") is False
        and s.get("publication_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and s.get("ingress_checks", {}).get("private_material_not_in_public_release") is True
        for s in signal_ingresses
    ) if signal_ingresses else True
    if signal_refs:
        late_change_refs.extend(signal_refs)
    remedy_resolutions = remedy_resolutions or []
    remedy_resolution_refs = remedy_resolution_refs or []
    unresolved_remedy_states = {
        "blocked-notice-dispatch-not-ready",
        "blocked-remedy-window-still-open",
        "blocked-remedy-submissions-unretained",
        "blocked-resolution-authority-missing",
        "blocked-resolution-decision-missing",
        "blocked-private-material-in-public-resolution",
    }
    unresolved_remedy_resolutions = [
        r.get("late_change_remedy_resolution_id", "unknown")
        for r in remedy_resolutions
        if r.get("decision", {}).get("remedy_resolution_state") in unresolved_remedy_states
    ]
    remedy_resolution_replayed = all(
        r.get("no_direct_floor_effect") is True
        and r.get("resolution_freeze_locks", {}).get("may_continue_published_snapshot_from_resolution") is False
        and r.get("resolution_freeze_locks", {}).get("may_increment_live_floor_from_resolution") is False
        and r.get("resolution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("resolution_freeze_locks", {}).get("remedy_silence_counts_as_waiver") is False
        and r.get("resolution_checks", {}).get("private_material_not_in_public_release") is True
        for r in remedy_resolutions
    ) if remedy_resolutions else True
    if remedy_resolution_refs:
        late_change_refs.extend(remedy_resolution_refs)
    remedy_executions = remedy_executions or []
    remedy_execution_refs = remedy_execution_refs or []
    unresolved_execution_states = {
        "blocked-remedy-resolution-not-ready",
        "blocked-execution-pending",
        "blocked-corrective-actions-incomplete",
        "blocked-execution-proof-missing",
        "blocked-private-material-in-public-execution",
    }
    unresolved_remedy_executions = [
        e.get("late_change_remedy_execution_id", "unknown")
        for e in remedy_executions
        if e.get("decision", {}).get("remedy_execution_state") in unresolved_execution_states
    ]
    remedy_execution_replayed = all(
        e.get("no_direct_floor_effect") is True
        and e.get("execution_freeze_locks", {}).get("may_continue_published_snapshot_from_execution") is False
        and e.get("execution_freeze_locks", {}).get("may_increment_live_floor_from_execution") is False
        and e.get("execution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and e.get("execution_freeze_locks", {}).get("execution_silence_counts_as_completion") is False
        and e.get("execution_checks", {}).get("private_material_not_in_public_release") is True
        for e in remedy_executions
    ) if remedy_executions else True
    ready_live_resolution_refs = [
        remedy_resolution_refs[i] if i < len(remedy_resolution_refs) else r.get("late_change_remedy_resolution_id", "unknown")
        for i, r in enumerate(remedy_resolutions)
        if r.get("remedy_context", {}).get("live_late_signal_present") is True
        and r.get("decision", {}).get("remedy_resolution_state") == "resolution-ready-publication-stayed"
    ]
    execution_linked_resolution_refs = {e.get("linked_late_change_remedy_resolution_ref") for e in remedy_executions}
    all_ready_remedies_have_execution = all(ref in execution_linked_resolution_refs for ref in ready_live_resolution_refs)
    if remedy_execution_refs:
        late_change_refs.extend(remedy_execution_refs)
    adjudication_checks = {
        "recompute_receipt_current_revision": recompute_receipt.get("revision") == revision,
        "recompute_receipt_publishable": decision.get("may_publish_snapshot") is True and checks.get("snapshot_matches_fresh_recompute") is True,
        "snapshot_hash_matches_recompute_receipt": snapshot_hash_matches,
        "all_late_challenges_replayed": all(c.get("recheck_matrix", {}).get("quorum_recomputed_after_rollback") is True for c in challenges) if challenges else True,
        "all_late_signal_ingress_replayed": signal_ingress_replayed,
        "no_unresolved_late_signal_ingress": not unresolved_signal_ingresses,
        "all_late_remedy_resolutions_replayed": remedy_resolution_replayed,
        "no_unresolved_late_remedy_resolution": not unresolved_remedy_resolutions,
        "all_late_remedy_executions_replayed": remedy_execution_replayed,
        "no_unresolved_late_remedy_execution": not unresolved_remedy_executions,
        "all_ready_late_remedies_have_execution_record": all_ready_remedies_have_execution,
        "no_open_challenge": not open_challenges,
        "no_uncompleted_upheld_rollback": not uncompleted_rollbacks,
        "supersession_rechecked": not simulate_supersession_open,
        "failed_gate_summaries_ready": challenge_summaries_ready,
        "public_notice_ready": challenge_summaries_ready and locks.get("rollback_recheck_required") is True,
        "manual_publication_override_absent": locks.get("manual_live_floor_update_allowed") is False and locks.get("may_increment_live_floor_from_receipt") is False,
        "recompute_required_after_any_late_change": locks.get("rollback_recheck_required") is True,
        "private_material_not_in_public_release": all("private-vault://" not in str(v) for v in [recompute_receipt_ref, snapshot_ref, *late_change_refs]),
    }
    if not adjudication_checks["recompute_receipt_publishable"] or not adjudication_checks["recompute_receipt_current_revision"]:
        state = "blocked-recompute-receipt-not-publishable"
    elif not adjudication_checks["snapshot_hash_matches_recompute_receipt"]:
        state = "blocked-snapshot-hash-mismatch"
    elif not adjudication_checks["no_open_challenge"]:
        state = "blocked-open-challenge"
    elif not adjudication_checks["no_uncompleted_upheld_rollback"]:
        state = "blocked-rollback-required"
    elif not adjudication_checks["all_late_signal_ingress_replayed"] or not adjudication_checks["no_unresolved_late_signal_ingress"]:
        state = "blocked-late-change-ingress-open"
    elif not adjudication_checks["all_late_remedy_resolutions_replayed"] or not adjudication_checks["no_unresolved_late_remedy_resolution"]:
        state = "blocked-late-change-remedy-resolution-open"
    elif not adjudication_checks["all_ready_late_remedies_have_execution_record"]:
        state = "blocked-remedy-resolution-unexecuted"
    elif not adjudication_checks["all_late_remedy_executions_replayed"] or not adjudication_checks["no_unresolved_late_remedy_execution"]:
        state = "blocked-late-change-remedy-execution-open"
    elif not adjudication_checks["supersession_rechecked"]:
        state = "blocked-supersession-unreplayed"
    elif summary.get("cross_critical_quorum_satisfied") is True and decision.get("may_upgrade_reliance") is True:
        state = "eligible-reliance-unchanged"
    elif summary.get("independent_receipts_present", 0) > 0:
        state = "eligible-class-local-stayed"
    else:
        state = "eligible-zero-floor-stayed"
    may_continue = state.startswith("eligible-")
    may_upgrade = state == "eligible-reliance-unchanged"
    blocked_reasons = [k for k, v in adjudication_checks.items() if v is not True]
    if state == "eligible-zero-floor-stayed":
        reason = "Floor recompute receipt is current and hash-bound; completed rollback/challenge records are replayed; live floor remains zero and reliance stayed."
    elif state == "eligible-class-local-stayed":
        reason = "Publication may continue only as class-local evidence; cross-critical reliance remains stayed."
    elif state == "eligible-reliance-unchanged":
        reason = "All post-publication rollback checks passed after a full quorum recompute receipt."
    else:
        reason = "Publication rollback adjudication blocked: " + "; ".join(blocked_reasons)
    return {
        "publication_adjudication_id": f"LRPRA-2026-{safe_slug(receipt_id)}",
        "schema_version": "live-receipt-publication-rollback-adjudication-v0.1",
        "created_at": created_at,
        "revision": revision,
        "linked_floor_recompute_receipt_ref": recompute_receipt_ref,
        "linked_computed_snapshot_ref": snapshot_ref,
        "computed_snapshot_sha256": snapshot_hash,
        "late_change_refs": late_change_refs,
        "observed_publication_summary": {
            "floor_publication_state": decision.get("floor_publication_state", "blocked"),
            "independent_receipts_present": int(summary.get("independent_receipts_present", 0)),
            "live_floor_delta": int(summary.get("live_floor_delta", 0)),
            "cross_critical_quorum_satisfied": bool(summary.get("cross_critical_quorum_satisfied", False)),
            "reliance_effect": summary.get("reliance_effect", "blocked"),
            "may_publish_snapshot": bool(decision.get("may_publish_snapshot")),
            "may_upgrade_reliance": bool(decision.get("may_upgrade_reliance")),
        },
        "adjudication_checks": adjudication_checks,
        "publication_rollback_locks": {
            "may_continue_published_snapshot": may_continue,
            "may_continue_reliance_posture": may_continue,
            "may_upgrade_reliance": may_upgrade,
            "may_increment_live_floor_from_adjudication": False,
            "manual_publication_override_allowed": False,
            "recompute_receipt_required_after_late_change": True,
            "late_challenge_reopens_publication": True,
        },
        "decision": {
            "publication_adjudication_state": state,
            "may_publish_or_continue_snapshot": may_continue,
            "may_upgrade_reliance": may_upgrade,
            "reliance_effect_after_adjudication": "ordinary-reliance" if may_upgrade else ("stayed" if may_continue else "blocked"),
            "reason": reason,
            "blocked_actions": [
                "continuing a published floor snapshot after open challenge without recomputation",
                "treating completed rollback as optional historical note",
                "manual reliance continuation after late supersession or revocation",
                "treating a late-change ingress as an informal note outside recompute",
                "treating remedy resolution as remedy execution or publication continuation",
                "live-floor increment from adjudication record",
            ],
            "next_actions": [
                "rerun compute_live_receipt_floor.py, floor recompute receipt, and publication rollback adjudication after any late challenge, rollback, revocation, supersession, correction, authority withdrawal, or hash mismatch",
                "create or repair a late-change ingress record before treating a signal as adjudicated",
                "execute any resolved rollback, correction, or supersession through a remedy execution record before continuation",
                "publish failed-gate summary and subject/counterparty notice for every rollback-affecting late change",
            ],
        },
        "no_direct_floor_effect": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute-receipt", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--receipt-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--simulate-supersession-open", action="store_true")
    args = parser.parse_args()
    revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    receipt_path = Path(args.recompute_receipt)
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt = load(receipt_path)
    snapshot_ref = receipt.get("linked_computed_snapshot_ref", "")
    snapshot_path = ROOT / snapshot_ref
    snapshot = load(snapshot_path) if snapshot_ref and snapshot_path.exists() else None
    snapshot_hash = sha256_json(snapshot) if snapshot else "0" * 64
    challenge_paths = sorted((ROOT / "examples").glob("receipt-import-challenge-rollback-record*.json"))
    challenges = [load(p) for p in challenge_paths]
    challenge_refs = [_rel(p) for p in challenge_paths]
    signal_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-ingress-record*.json"))
    signal_ingresses = [load(p) for p in signal_paths]
    signal_refs = [_rel(p) for p in signal_paths]
    remedy_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-remedy-resolution-record*.json"))
    remedy_resolutions = [load(p) for p in remedy_paths]
    remedy_refs = [_rel(p) for p in remedy_paths]
    execution_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-remedy-execution-record*.json"))
    remedy_executions = [load(p) for p in execution_paths]
    execution_refs = [_rel(p) for p in execution_paths]
    record = build(
        recompute_receipt=receipt,
        recompute_receipt_ref=_rel(receipt_path),
        snapshot=snapshot,
        snapshot_ref=snapshot_ref,
        snapshot_hash=snapshot_hash,
        challenges=challenges,
        challenge_refs=challenge_refs,
        receipt_id=args.receipt_id,
        created_at=args.created_at,
        revision=revision,
        simulate_supersession_open=args.simulate_supersession_open,
        signal_ingresses=signal_ingresses,
        signal_refs=signal_refs,
        remedy_resolutions=remedy_resolutions,
        remedy_resolution_refs=remedy_refs,
        remedy_executions=remedy_executions,
        remedy_execution_refs=execution_refs,
    )
    out = Path(args.output_dir) / f"live-receipt-publication-rollback-adjudication-{safe_slug(args.receipt_id)}.json"
    write(out, record)
    print(out)


if __name__ == "__main__":
    main()
