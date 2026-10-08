#!/usr/bin/env python3
"""Build a public send-attempt transaction ledger for the current reviewer-first path.

This tool is intentionally no-send: it has no network code and it refuses to
represent templates, route facts, or dry-run hashes as authority. Its useful job
is to make the final pre-action state machine explicit and reproducible.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def rel(name: str) -> str:
    return f"examples/{name}"


def sha_bytes(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def body_hash_and_word_count(path: str):
    body = (ROOT / path).read_text(encoding="utf-8").strip()
    return hashlib.sha256(body.encode("utf-8")).hexdigest(), len(body.split())


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build(created_at: str):
    source_refs = {
        "current_action_spine": rel(f"current-action-spine-{REV}-reviewer-first-no-send.json"),
        "last_mile_operator_checklist": rel(f"last-mile-operator-checklist-{REV}-reviewer-first-no-send.json"),
        "pre_send_evidence_bundle": rel(f"pre-send-evidence-bundle-{REV}-reviewer-first-no-send.json"),
        "authority_expiry_and_renewal_check": rel(f"authority-expiry-and-renewal-check-{REV}-no-signature.json"),
        "authority_handoff_vault_dry_run": rel(f"authority-handoff-vault-dry-run-{REV}-reviewer-first-nosend.json"),
        "operator_identity_signature_template": rel(f"operator-identity-signature-capture-template-{REV}-no-signature.json"),
        "private_root_selection_dryrun_shell": rel(f"private-root-selection-dryrun-shell-{REV}-no-private-root.json"),
        "pre_send_custody_precommit": rel(f"pre-send-custody-precommit-{REV}-no-private-root-selected.json"),
        "signed_authority_public_shell_template": rel(f"signed-authority-public-shell-{REV}-template.json"),
        "human_branch_decision_template": rel(f"human-branch-decision-record-{REV}-unsigned-template.json"),
        "route_locator_freshness_ledger": rel(f"route-locator-freshness-ledger-{REV}-public-source-no-contact.json"),
        "reviewer_first_packet": rel(f"reviewer-first-contact-packet-{REV}-eleos-not-sent.json"),
        "reviewer_first_body": rel(f"reviewer-first-contact-body-{REV}-eleos-not-sent.txt"),
        "reviewer_first_mail_ready_draft": rel(f"reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"),
        "response_disposition_playbook": rel(f"reviewer-response-disposition-playbook-{REV}.json"),
        "failed_gate_public_summary_template": rel(f"failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"),
        "field_artifact_capture_workbook": rel(f"field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"),
        "six_artifact_pilot_state": rel(f"six-artifact-pilot-state-{REV}-preservation-review.json"),
    }
    for label, path in source_refs.items():
        if not (ROOT / path).exists():
            raise SystemExit(f"missing source for {label}: {path}")

    body_sha, body_words = body_hash_and_word_count(source_refs["reviewer_first_body"])
    route = load_json(source_refs["route_locator_freshness_ledger"])
    auth = load_json(source_refs["authority_expiry_and_renewal_check"])
    private_root = load_json(source_refs["private_root_selection_dryrun_shell"])
    operator_sig = load_json(source_refs["operator_identity_signature_template"])

    hash_bindings = {f"{key}_sha256": sha_bytes(path) for key, path in source_refs.items()}
    hash_bindings["reviewer_first_body_text_sha256"] = body_sha
    hash_bindings["reviewer_first_body_word_count"] = body_words
    hash_bindings["send_time_hash_recompute_performed"] = False
    hash_bindings["dry_run_may_satisfy_send_time_hash_recompute"] = False

    gate_results = [
        {
            "gate_id": "G0-CURRENT-HEAD",
            "required_before": "operator action",
            "observed_state": "current rev surfaces exist and are hash-bound in this public ledger",
            "result": "pass-for-orientation-only-not-authority",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G1-OPERATOR-IDENTITY-AND-SIGNATURE",
            "required_before": "any branch selection",
            "observed_state": "missing private operator identity proof and missing private branch signature",
            "result": "abort-no-send",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G2-PRIVATE-ROOT-SELECTION",
            "required_before": "any send or response-clock claim",
            "observed_state": "no private roots selected; public shell records only required root classes",
            "result": "abort-no-send",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G3-ROUTE-FRESHNESS",
            "required_before": "send-time branch execution",
            "observed_state": f"route ledger checked at {route.get('freshness_policy', {}).get('checked_at_utc')} and expires at {route.get('freshness_policy', {}).get('freshness_expires_at_utc')}; public locator is still not consent",
            "result": "pass-for-routing-only-not-authority",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G4-AUTHORITY-EXPIRY",
            "required_before": "one-shot send window",
            "observed_state": "no signature, no branch value, no send window open",
            "result": "abort-no-send",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G5-SEND-TIME-HASH-RECOMPUTE",
            "required_before": "transmission",
            "observed_state": "current public hashes computed now, but send-time recompute has not occurred because no signature/root exists",
            "result": "abort-no-send",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G6-TRANSPORT-CAPTURE",
            "required_before": "delivery or failed-send claim",
            "observed_state": "missing because no transmission occurred",
            "result": "not-reached-no-send",
            "abort_if_failed": True,
        },
        {
            "gate_id": "G7-RESPONSE-DISPOSITION",
            "required_before": "any response, referral, decline, silence, or failed-gate public summary",
            "observed_state": "not reached because no contact; playbook available for future classification only",
            "result": "not-reached-no-contact",
            "abort_if_failed": True,
        },
    ]
    return {
        "transaction_id": f"SATL-2026-{REV}-reviewer-first-aborted-no-signature",
        "schema_version": "send-attempt-transaction-ledger-v0.1-ad-hoc",
        "revision": REV,
        "created_at": created_at,
        "transaction_state": "aborted-before-send-no-signature-no-private-root-no-contact",
        "risk_addressed": "The archive had an action spine, but a real operator still needed a single public transaction ledger that records the last-mile gates as pass/abort/not-reached without turning a dry-run into authority.",
        "attempted_action": "evaluate whether one exact reviewer-first send could be authorized",
        "current_result": "NO-SEND-FAIL-CLOSED",
        "why_not_completed": [
            "no private operator identity/signature record",
            "no signed branch value",
            "no selected private roots outside the release tree",
            "no send-time hash recompute tied to a live signature window",
            "no transport proof because no message was sent",
            "no response classification because no counterparty was contacted",
        ],
        "source_refs": source_refs,
        "hash_bindings": hash_bindings,
        "gate_results": gate_results,
        "private_input_status": {
            "operator_identity_template_state": operator_sig.get("template_state"),
            "private_signature_present": False,
            "signed_branch_value_present": False,
            "signature_window_open": False,
            "private_root_shell_state": private_root.get("shell_state"),
            "selected_private_roots_count": 0,
            "public_tree_contains_private_root_paths": False,
        },
        "future_completion_conditions": [
            "private operator identity proof and private branch signature captured outside the public release tree",
            "branch value is no-send, defer, stop, or one exact reviewer-first send",
            "private roots selected for sent copy, transport proof, raw inbound, classification notes, and sealed evidence before send",
            "route locator refreshed immediately before send and still consistent with the signed branch",
            "message body, .eml, subject, recipient, sender account, attachment scope, and one-shot limit recomputed at send time",
            "transport result captured privately before public delivery/failure summary",
            "any response, auto-ack, referral, decline, silence, or private-data request classified before public narration",
        ],
        "overclaim_locks": {
            "ledger_may_authorize_send": False,
            "ledger_may_substitute_for_private_signature": False,
            "ledger_may_select_or_reveal_private_roots": False,
            "ledger_may_start_response_clock": False,
            "ledger_may_count_as_transport_delivery_response_custody_intake_import_or_floor": False,
            "ledger_may_claim_reviewer_appointment_or_welfare_finding": False,
        },
        "no_contact_state": {
            "message_sent": False,
            "counterparty_contacted": False,
            "response_clock_started": False,
            "raw_inbound_artifact_exists": False,
            "live_floor_effect": 0,
        },
        "no_live_floor_effect": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(args.created_at), indent=2) + "\n", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
