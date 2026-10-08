#!/usr/bin/env python3
"""Prepare a pre-custody authority gate from a candidate challenge report.

This gate is intentionally narrower than a custody record. It decides whether a
counterparty-artifact-custody-record may be prepared, while keeping response,
intake, import, and live-floor effects locked.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_CREATED_AT = "2026-06-16T19:06:00Z"
RECEIPT_CLASSES = [
    "first-touch-clock",
    "continuity-compute-floor",
    "sealed-public-parity",
    "namespace-cache",
    "reserve-ledger",
    "representative-contact",
    "witness-dependency",
    "welfare-signal-integrity",
    "independent-review",
    "result-return",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def safe_slug(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_", ".", ":"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out).strip(".-_:") or "custody-gate"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--challenge-report", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--created-at", default=DEFAULT_CREATED_AT)
    parser.add_argument("--challenge-status", choices=["open", "blocked", "closed-no-objection", "closed-upheld", "closed-rejected"], default=None, help="Legacy/status-display override only. Closed statuses cannot make the gate eligible unless --challenge-disposition-record is supplied.")
    parser.add_argument("--challenge-disposition-record", help="Human-reviewed candidate-challenge disposition record. Required before any closed challenge status can make custody-record preparation eligible.")
    parser.add_argument("--authority-evidence-binder", help="Evidence binder with cited authority refs. Required before authority-looking booleans can make custody-record preparation eligible.")
    parser.add_argument("--receipt-class", choices=RECEIPT_CLASSES, default="result-return")
    parser.add_argument("--counterparty-org-id")
    parser.add_argument("--dependency-group-id")
    parser.add_argument("--authority-basis", default="not supplied")
    parser.add_argument("--authority-scope", action="append", default=[])
    parser.add_argument("--authority-limitation", action="append", default=[])
    parser.add_argument("--manual-counterparty-contact-confirmed", action="store_true")
    parser.add_argument("--request-trace-confirmed", action="store_true")
    parser.add_argument("--subject-or-representative-authority-verified", action="store_true")
    parser.add_argument("--verifier-adapter-ref")
    parser.add_argument("--independent-timestamp-ref")
    parser.add_argument("--nonhost-retention-ref")
    parser.add_argument("--sealed-public-parity-ref")
    parser.add_argument("--redaction-boundary-ref")
    parser.add_argument("--dependency-group-independence-checked", action="store_true")
    parser.add_argument("--authority-limitations-published", action="store_true")
    args = parser.parse_args()

    challenge_path = Path(args.challenge_report).expanduser().resolve()
    challenge = load_json(challenge_path)
    ch_window = challenge.get("challenge_window", {})
    ch_vault = challenge.get("vault_reread", {})
    disposition_path = Path(args.challenge_disposition_record).expanduser().resolve() if args.challenge_disposition_record else None
    disposition = load_json(disposition_path) if disposition_path else None
    binder_path = Path(args.authority_evidence_binder).expanduser().resolve() if args.authority_evidence_binder else None
    binder = load_json(binder_path) if binder_path else None
    binder_decision = binder.get("decision", {}) if binder else {}
    binder_locks = binder.get("downstream_locks", {}) if binder else {}
    binder_bound = bool(
        binder
        and binder.get("no_live_floor_effect") is True
        and binder.get("receipt_class") == args.receipt_class
        and (not args.counterparty_org_id or binder.get("counterparty_org_id") in {args.counterparty_org_id, None})
        and (not args.dependency_group_id or binder.get("dependency_group_id") in {args.dependency_group_id, None})
    )
    binder_may_feed = bool(
        binder_bound
        and binder.get("binder_state") == "verified-for-custody-gate"
        and binder_decision.get("authority_evidence_complete") is True
        and binder_decision.get("receipt_class_authority_scoped") is True
        and binder_decision.get("may_feed_custody_authority_gate") is True
        and binder_locks.get("custody_gate_may_consume_binder") is True
    )
    raw_status_override_used = bool(args.challenge_status and disposition is None)
    if disposition:
        disposition_decision = disposition.get("decision", {})
        challenge_status = disposition_decision.get("challenge_status_effective") or ch_window.get("status") or "blocked"
    else:
        disposition_decision = {}
        challenge_status = args.challenge_status or ch_window.get("status") or "blocked"

    disposition_bound = bool(
        disposition
        and disposition.get("no_live_floor_effect") is True
        and disposition.get("source_challenge_report_ref")
        and (
            disposition.get("candidate_challenge_snapshot", {}).get("challenge_report_id") == challenge.get("challenge_report_id")
        )
    )
    disposition_may_feed = bool(disposition_bound and disposition_decision.get("may_feed_custody_authority_gate") is True)
    closed_status_without_disposition = challenge_status in {"closed-no-objection", "closed-rejected", "closed-upheld"} and not disposition_may_feed

    candidate_integrity_ok = (
        challenge.get("candidate_state") == "hash-reverified-challenge-pending"
        and ch_vault.get("vault_reread_performed") is True
        and ch_vault.get("hash_reverified") is True
        and ch_vault.get("size_reverified") is True
        and ch_vault.get("public_shell_bound") is True
        and challenge.get("no_live_floor_effect") is True
    )
    challenge_window_resolved = challenge_status in {"closed-no-objection", "closed-rejected"}
    challenge_upheld = challenge_status == "closed-upheld"
    receipt_class_authority_scoped = bool(args.authority_scope and args.receipt_class in set(args.authority_scope))
    authority_verified = bool(args.subject_or_representative_authority_verified and receipt_class_authority_scoped and binder_may_feed)
    prereq = {
        "challenge_window_resolved": challenge_window_resolved,
        "manual_counterparty_contact_confirmed": bool(args.manual_counterparty_contact_confirmed),
        "request_trace_confirmed": bool(args.request_trace_confirmed),
        "subject_or_representative_authority_verified": bool(args.subject_or_representative_authority_verified),
        "receipt_class_authority_scoped": receipt_class_authority_scoped,
        "verifier_adapter_bound": bool(args.verifier_adapter_ref),
        "independent_timestamp_bound": bool(args.independent_timestamp_ref),
        "nonhost_retention_confirmed": bool(args.nonhost_retention_ref),
        "sealed_public_parity_confirmed": bool(args.sealed_public_parity_ref),
        "redaction_boundary_confirmed": bool(args.redaction_boundary_ref),
        "dependency_group_independence_checked": bool(args.dependency_group_independence_checked),
        "authority_limitations_published": bool(args.authority_limitations_published),
    }
    unresolved = []
    if not candidate_integrity_ok:
        gate_state = "blocked-candidate-integrity"
        unresolved.append("candidate challenge integrity failed or vault reread absent")
    elif challenge_status == "open":
        gate_state = "blocked-challenge-pending"
        unresolved.append("challenge window remains open; silence is not waiver")
    elif challenge_upheld:
        gate_state = "blocked-challenge-upheld"
        unresolved.append("challenge was upheld")
    elif closed_status_without_disposition:
        gate_state = "blocked-missing-authority"
        unresolved.append("candidate_challenge_disposition_record")
        if raw_status_override_used:
            unresolved.append("raw_challenge_status_override_blocked")
    elif not all(prereq.values()) or not authority_verified or not args.counterparty_org_id or not args.dependency_group_id or not binder_may_feed:
        gate_state = "blocked-missing-authority"
        for k, v in prereq.items():
            if not v:
                unresolved.append(k)
        if not args.counterparty_org_id:
            unresolved.append("counterparty_org_id")
        if not args.dependency_group_id:
            unresolved.append("dependency_group_id")
        if not binder_may_feed:
            unresolved.append("custody_authority_evidence_binder")
        if not authority_verified:
            unresolved.append("authority_verified")
    else:
        gate_state = "eligible-for-custody-record"

    eligible = gate_state == "eligible-for-custody-record"
    slug = safe_slug(args.gate_id)
    report = {
        "custody_gate_id": f"CACG-2026-{slug}",
        "schema_version": "counterparty-artifact-custody-gate-v0.1",
        "revision": REV,
        "created_at": args.created_at,
        "generated_by_tool": "tools/prepare_custody_authority_gate.py",
        "linked_candidate_challenge_report_ref": str(challenge_path),
        "gate_state": gate_state,
        "candidate_challenge": {
            "challenge_report_id": challenge.get("challenge_report_id"),
            "candidate_state": challenge.get("candidate_state"),
            "challenge_status": challenge_status,
            "vault_reread_performed": ch_vault.get("vault_reread_performed") is True,
            "hash_reverified": ch_vault.get("hash_reverified") is True,
            "size_reverified": ch_vault.get("size_reverified") is True,
            "public_shell_bound": ch_vault.get("public_shell_bound") is True,
            "silence_treated_as_waiver": False,
            "challenge_pending_stays_reliance": ch_window.get("challenge_pending_stays_reliance") is True,
        },
        "challenge_disposition": {
            "disposition_record_ref": str(disposition_path) if disposition_path else None,
            "disposition_record_id": disposition.get("disposition_record_id") if disposition else None,
            "disposition_state": disposition.get("disposition_state") if disposition else None,
            "challenge_status_effective": challenge_status,
            "may_feed_custody_authority_gate": disposition_may_feed,
            "raw_status_override_used": raw_status_override_used,
            "status_override_without_disposition_blocked": closed_status_without_disposition,
        },
        "custody_prerequisites": prereq,
        "authority_evidence_binder": {
            "binder_ref": str(binder_path) if binder_path else None,
            "binder_id": binder.get("binder_id") if binder else None,
            "binder_state": binder.get("binder_state") if binder else None,
            "authority_evidence_complete": binder_decision.get("authority_evidence_complete") is True,
            "receipt_class_authority_scoped": binder_decision.get("receipt_class_authority_scoped") is True,
            "may_feed_custody_authority_gate": bool(eligible and binder_may_feed),
            "checkbox_only_authority_blocked": not bool(eligible and binder_may_feed),
        },
        "class_authority": {
            "receipt_class": args.receipt_class,
            "counterparty_org_id": args.counterparty_org_id,
            "dependency_group_id": args.dependency_group_id,
            "authority_basis": args.authority_basis,
            "authority_scope": args.authority_scope or ["none-supplied"],
            "authority_limitations": args.authority_limitation or ["no authority limitations supplied; gate cannot open unless limitations are published"],
            "authority_verified": authority_verified,
            "unresolved_challenges": unresolved,
        },
        "downstream_locks": {
            "may_prepare_counterparty_artifact_custody_record": eligible,
            "custody_record_admitted": False,
            "response_creation_allowed": False,
            "intake_creation_allowed": False,
            "import_gate_creation_allowed": False,
            "live_floor_delta_allowed": False,
            "locks_release_only_after": [
                "a separate counterparty-artifact-custody-record is prepared and passes raw locator/hash/authority checks",
                "a response record is created from the custody record and verified independently",
                "an intake record accepts the response without treating silence or absence as waiver",
                "an actual-receipt-import-gate binds LEAP, custody, response, intake, verifier adapter, timestamp, and non-host retention",
                "the computed live-floor engine recomputes from eligible actual-live imports only",
            ],
        },
        "decision": {
            "custody_record_may_be_prepared": eligible,
            "custody_record_is_created_by_this_gate": False,
            "reliance_effect": "stayed",
            "blocked_actions": [
                "create response, intake, import, or floor delta from this gate",
                "treat closed-no-objection as waiver without manual counterparty contact and request trace",
                "treat a raw challenge-status override as disposition evidence",
                "treat receipt-class authority as global authority",
                "treat verifier/timestamp/non-host booleans as satisfied without evidence refs",
                "treat authority-looking booleans as custody authority without a custody-authority-evidence-binder",
            ],
            "next_actions": [
                "if eligible, prepare a separate counterparty-artifact-custody-record with raw hash/locator binding and no source-path disclosure",
                "before eligibility, bind a custody-authority-evidence-binder with class-scoped evidence refs",
                "if the challenge status is closed, require a candidate-challenge-disposition-record before treating it as gate input",
                "if blocked, publish or maintain a failed-gate shell and keep the candidate out of response/intake/import",
                "rerun admission graph, invariant report, and computed live floor after any real custody object is added",
            ],
            "reason": (
                "challenge resolved and authority/integrity prerequisites plus evidence binder satisfied; custody record may be prepared but no downstream reliance is created"
                if eligible else
                "candidate challenge has not cleared the custody authority gate; reliance remains stayed and downstream objects are locked"
            ),
        },
        "public_summary": f"{REV} custody authority gate state={gate_state}; it may only authorize a separate custody record and never creates response, intake, import, or live-floor credit.",
        "no_live_floor_effect": True,
    }
    out_dir = Path(args.output_dir).expanduser().resolve()
    out = out_dir / f"counterparty-artifact-custody-gate-{slug}.json"
    write_json(out, report)
    print(out)


if __name__ == "__main__":
    main()
