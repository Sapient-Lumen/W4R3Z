#!/usr/bin/env python3
"""Compile the public operator-authority packet for the current no-send path.

This builder deliberately has no network, email, filesystem side effects outside the
public release tree, or signature-handling code. It only proves what a future
human operator must bind privately before the action can move from prepared to
authorized.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def rel(name: str) -> str:
    return f"examples/{name}"


def sha256(rel_path: str) -> str:
    return hashlib.sha256((ROOT / rel_path).read_bytes()).hexdigest()


def load(rel_path: str):
    return json.loads((ROOT / rel_path).read_text(encoding="utf-8"))


def body_hash_and_word_count(rel_path: str):
    body = (ROOT / rel_path).read_text(encoding="utf-8").strip()
    return hashlib.sha256(body.encode("utf-8")).hexdigest(), len(body.split())


def build(created_at: str):
    source_refs = {
        "send_attempt_transaction_ledger": rel(f"send-attempt-transaction-ledger-{REV}-no-signature-aborted.json"),
        "current_action_spine": rel(f"current-action-spine-{REV}-reviewer-first-no-send.json"),
        "last_mile_operator_checklist": rel(f"last-mile-operator-checklist-{REV}-reviewer-first-no-send.json"),
        "pre_send_evidence_bundle": rel(f"pre-send-evidence-bundle-{REV}-reviewer-first-no-send.json"),
        "operator_identity_signature_template": rel(f"operator-identity-signature-capture-template-{REV}-no-signature.json"),
        "private_root_selection_dryrun_shell": rel(f"private-root-selection-dryrun-shell-{REV}-no-private-root.json"),
        "human_branch_decision_template": rel(f"human-branch-decision-record-{REV}-unsigned-template.json"),
        "signed_authority_public_shell_template": rel(f"signed-authority-public-shell-{REV}-template.json"),
        "authority_expiry_and_renewal_check": rel(f"authority-expiry-and-renewal-check-{REV}-no-signature.json"),
        "authority_handoff_vault_dry_run": rel(f"authority-handoff-vault-dry-run-{REV}-reviewer-first-nosend.json"),
        "pre_send_custody_precommit": rel(f"pre-send-custody-precommit-{REV}-no-private-root-selected.json"),
        "route_locator_freshness_ledger": rel(f"route-locator-freshness-ledger-{REV}-public-source-no-contact.json"),
        "reviewer_route_due_diligence_matrix": rel(f"reviewer-route-due-diligence-matrix-{REV}-public-source-no-contact.json"),
        "reviewer_first_packet": rel(f"reviewer-first-contact-packet-{REV}-eleos-not-sent.json"),
        "reviewer_first_body": rel(f"reviewer-first-contact-body-{REV}-eleos-not-sent.txt"),
        "reviewer_first_mail_ready_draft": rel(f"reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"),
        "response_disposition_playbook": rel(f"reviewer-response-disposition-playbook-{REV}.json"),
        "failed_gate_public_summary_template": rel(f"failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"),
        "field_artifact_capture_workbook": rel(f"field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"),
        "six_artifact_pilot_state": rel(f"six-artifact-pilot-state-{REV}-preservation-review.json"),
    }

    missing = [path for path in source_refs.values() if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError("missing authority packet source(s): " + ", ".join(missing))

    route = load(source_refs["route_locator_freshness_ledger"])
    identity = load(source_refs["operator_identity_signature_template"])
    roots = load(source_refs["private_root_selection_dryrun_shell"])
    transaction = load(source_refs["send_attempt_transaction_ledger"])
    bundle = load(source_refs["pre_send_evidence_bundle"])
    spine = load(source_refs["current_action_spine"])

    hash_bindings = {f"{key}_sha256": sha256(path) for key, path in source_refs.items()}
    body_hash, body_words = body_hash_and_word_count(source_refs["reviewer_first_body"])
    hash_bindings["reviewer_first_body_normalized_sha256"] = body_hash
    hash_bindings["reviewer_first_body_word_count"] = body_words

    route_policy = route.get("freshness_policy", {})
    private_values = identity.get("current_values", {})
    selected_roots = [r for r in roots.get("required_private_roots", []) if r.get("selected")]

    gate_results = [
        {
            "gate_id": "C0-COMPILE-CURRENT-SOURCES",
            "observed_state": "all public current source refs exist and are hash-bound in this packet",
            "result": "pass-for-public-compilation-only",
            "may_authorize_action": False,
        },
        {
            "gate_id": "C1-OPERATOR-AUTHORITY",
            "observed_state": identity.get("template_state"),
            "required_private_delta": "private identity/role proof, branch value, timestamp, expiry, and signature record outside the public tree",
            "result": "fail-closed-no-signature",
            "may_authorize_action": False,
        },
        {
            "gate_id": "C2-PRIVATE-ROOTS",
            "observed_state": roots.get("shell_state"),
            "required_private_delta": "select private roots for raw sent copy, transport proof, raw inbound, classification notes, sealed evidence, and signature record",
            "result": "fail-closed-no-private-root",
            "may_authorize_action": False,
        },
        {
            "gate_id": "C3-ROUTE-FRESHNESS",
            "observed_state": f"checked_at={route_policy.get('checked_at_utc')} expires_at={route_policy.get('freshness_expires_at_utc')}",
            "required_private_delta": "recheck immediately before any signed send; route page is never consent",
            "result": "pass-for-routing-orientation-only",
            "may_authorize_action": False,
        },
        {
            "gate_id": "C4-EXACT-MESSAGE-HASHES",
            "observed_state": "public body and .eml hashes bound now; send-time recompute not reached",
            "required_private_delta": "recompute exact bytes inside live signature window against same recipient, subject, sender, body, and no-attachment scope",
            "result": "fail-closed-no-send-time-recompute",
            "may_authorize_action": False,
        },
        {
            "gate_id": "C5-TRANSACTION-LEDGER",
            "observed_state": transaction.get("current_result"),
            "required_private_delta": "only a non-aborted future transaction with signature, roots, route recheck, and transport capture can move A1/A2",
            "result": "fail-closed-current-transaction-aborted",
            "may_authorize_action": False,
        },
    ]

    return {
        "packet_id": f"OAPC-2026-{REV}-reviewer-first-public-compiler-no-signature",
        "schema_version": "operator-authority-packet-compiler-v0.1-ad-hoc",
        "revision": REV,
        "created_at": created_at,
        "packet_state": "compiled-public-dryrun-no-private-authority-no-send",
        "risk_addressed": "rev0271 recorded a public no-send transaction, but the final operator still needed a single compiled authority packet that binds the transaction, branch template, private-root shell, route freshness, exact message bytes, and response rules without becoming authority itself.",
        "current_compile_result": "NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY",
        "source_refs": source_refs,
        "hash_bindings": hash_bindings,
        "gate_results": gate_results,
        "private_input_state": {
            "operator_identity_record_present": bool(private_values.get("operator_identity_record_present")),
            "private_signature_record_present": bool(private_values.get("private_signature_record_present")),
            "branch_value_present": bool(private_values.get("branch_value_present")),
            "signature_window_open": bool(private_values.get("signature_window_open")),
            "selected_private_roots_count": len(selected_roots),
            "public_release_contains_private_identity_material": bool(private_values.get("public_release_contains_private_identity_material")),
            "public_tree_contains_private_root_paths": bool(roots.get("public_tree_checks", {}).get("private_paths_disclosed", False)),
        },
        "operator_delta_to_complete_A1_A2": [
            "privately sign exactly one branch: NO-SEND, DEFER, STOP, or ONE-SHOT-REVIEWER-FIRST-SEND",
            "select private roots outside the public release tree before any transmission",
            "refresh route locator and route-fit facts immediately before send",
            "recompute exact message body/.eml/subject/recipient/sender/no-attachment hashes inside the signature window",
            "record transport proof or failed-send proof privately before any public summary",
            "classify any response or silence under the disposition playbook before public narration",
        ],
        "abort_and_publication_rules": {
            "current_public_transaction_result": transaction.get("current_result"),
            "if_signature_absent": "publish or retain only no-send/fail-closed state; do not contact",
            "if_private_roots_absent": "abort even if signer wants send; custody would be unpreserved",
            "if_route_facts_expired_or_changed": "renew route ledger and authority before any send",
            "if_hashes_changed": "renew authority and packet; old signature cannot authorize changed bytes",
            "if_transport_fails": "may publish failed-gate summary only after private failed-send proof is captured",
            "if_auto_ack_or_silence": "must not claim human response, reviewer appointment, welfare finding, custody, intake, import, or live-floor effect",
        },
        "active_path_bindings": {
            "spine_state": spine.get("spine_state"),
            "bundle_state": bundle.get("bundle_state"),
            "transaction_state": transaction.get("transaction_state"),
            "route_freshness_expires_at_utc": route_policy.get("freshness_expires_at_utc"),
        },
        "overclaim_locks": {
            "packet_may_authorize_send": False,
            "packet_may_substitute_for_private_signature": False,
            "packet_may_select_or_reveal_private_roots": False,
            "packet_may_substitute_for_send_time_hash_recompute": False,
            "packet_may_start_response_clock": False,
            "packet_may_count_as_transport_delivery_response_custody_intake_import_or_floor": False,
            "packet_may_claim_reviewer_appointment_or_welfare_finding": False,
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
