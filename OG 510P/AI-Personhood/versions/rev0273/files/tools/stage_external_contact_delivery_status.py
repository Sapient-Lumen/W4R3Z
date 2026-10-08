#!/usr/bin/env python3
"""Stage external-contact delivery status/DSN evidence into a public shell.

Raw DSN/provider exports must remain outside the release tree. This tool can
hash an off-tree candidate and emit a shell, but it never treats DSNs, bounces,
delays, provider UI, or public shells as counterparty responses, authority,
custody, no-response clocks, or live-floor evidence.
"""
import argparse
import hashlib
import json
import mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_OUTPUT = ROOT / "examples" / f"external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json"


def _inside_release(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def predispatch_record() -> dict:
    return {
        "record_id": f"ECDSR-2026-{REV}-no-status",
        "schema_version": "external-contact-delivery-status-record-v0.1",
        "revision": REV,
        "created_at": "2026-06-16T22:58:00Z",
        "delivery_status_state": "pre-dispatch-no-delivery-status",
        "source_execution_record_ref": f"examples/external-contact-execution-record-{REV}-ready-to-dispatch.json",
        "source_send_proof_record_ref": f"examples/external-contact-send-proof-record-{REV}-no-transport-proof.json",
        "source_send_trace_shell_ref": f"examples/external-contact-send-trace-shell-{REV}-no-transport.json",
        "source_dispatch_authorization_card_ref": f"examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json",
        "source_response_triage_record_ref": f"examples/external-contact-response-triage-record-{REV}-pre-dispatch.json",
        "status_capture_tool": {
            "tool_path": "tools/stage_external_contact_delivery_status.py",
            "raw_input_required_outside_release_tree": True,
            "copy_to_private_vault_only": True,
            "public_shell_only": True,
            "check_output_supported": True,
            "tool_is_not_delivery_or_response": True
        },
        "candidate_delivery_status": {
            "raw_status_present_now": False,
            "source_locator": None,
            "private_status_locator": None,
            "raw_status_sha256": None,
            "size_bytes": None,
            "mime_type": None,
            "status_format": None,
            "dsn_action": None,
            "status_code": None,
            "diagnostic_code_present": False,
            "final_recipient_matches_selected_candidate": False,
            "original_message_id_or_envid_matches_sent_trace": False,
            "raw_status_publicly_embedded": False,
            "screenshot_only": False,
            "provider_ui_only": False,
            "counterparty_human_reply_present": False,
            "delivery_status_proof_present_now": False
        },
        "dsn_classification_rules": {
            "rfc3461_dsn_extension_is_transport_only": True,
            "rfc3464_message_delivery_status_is_transport_only": True,
            "failed_dsn_is_not_counterparty_decline": True,
            "delayed_dsn_is_not_no_response": True,
            "delivered_or_relayed_dsn_is_not_counterparty_response": True,
            "auto_generated_dsn_may_create_response_record": False,
            "dsn_may_create_custody": False,
            "dsn_may_create_authority": False,
            "dsn_may_increment_live_floor": False
        },
        "response_clock_policy": {
            "clock_may_start_now": False,
            "start_requires_signed_authorization": True,
            "start_requires_sent_at_utc": True,
            "start_requires_send_trace_transport_proof": True,
            "start_requires_send_proof_record_sent_state": True,
            "start_requires_no_failed_or_delayed_delivery_status": True,
            "start_may_use_delivery_status_timestamp_alone": False,
            "bounce_or_delay_suspends_no_response_claim": True,
            "no_response_may_be_recorded_now": False,
            "delivery_status_may_substitute_for_counterparty_reply": False
        },
        "delivery_outcome_decision": {
            "current_outcome": "not-applicable-pre-dispatch",
            "delivery_status_processed_now": False,
            "hard_bounce_requires_counterparty_or_channel_reselection": True,
            "delayed_status_requires_watch_not_no_response": True,
            "successful_delivery_is_not_human_response": True,
            "retry_or_reselection_may_create_failed_gate": False,
            "public_status_shell_allowed": True
        },
        "public_shell_policy": {
            "allowed_public_fields": [
                "record id", "revision", "delivery status state", "raw status sha256", "status size", "status format", "dsn action classification", "status code family", "source send-trace shell ref"
            ],
            "forbidden_public_fields": [
                "raw DSN bytes", "raw headers", "personal addresses", "provider account ids", "private vault locators", "authentication tokens", "counterparty-private content", "SMTP transcript details"
            ],
            "public_shell_may_publish_raw_dsn": False,
            "public_shell_may_publish_personal_headers": False,
            "public_shell_may_satisfy_delivery_proof": False,
            "private_raw_status_required_for_delivery_outcome": True,
            "public_shell_may_start_response_clock": False
        },
        "downstream_locks": {
            "may_treat_dsn_as_counterparty_response": False,
            "may_treat_bounce_as_decline": False,
            "may_treat_delay_as_no_response": False,
            "may_treat_delivered_as_human_reply": False,
            "may_start_response_clock": False,
            "may_create_failed_gate_shell_now": False,
            "may_create_response_record": False,
            "may_create_custody_record": False,
            "may_create_intake_record": False,
            "may_create_import_gate": False,
            "may_increment_live_floor": False,
            "may_claim_status_or_waiver": False,
            "may_publish_raw_delivery_status": False
        },
        "linked_queue_ids": ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"],
        "related_surfaces": [
            f"examples/external-contact-send-proof-record-{REV}-no-transport-proof.json",
            f"examples/external-contact-send-trace-shell-{REV}-no-transport.json",
            f"examples/external-contact-execution-record-{REV}-ready-to-dispatch.json",
            f"examples/external-contact-response-triage-record-{REV}-pre-dispatch.json",
            "tools/stage_external_contact_delivery_status.py",
            "tools/audit_external_contact_delivery_status_record.py",
            "schemas/external-contact-delivery-status-record.schema.json",
            "fixtures/negative-tests/external-contact-delivery-status-dsn-as-response.json"
        ],
        "public_summary": f"{REV} adds a delivery-status/DSN gate before any response-window or no-response evidence can be claimed. At this revision there is no sent message and no DSN, bounce, delay, successful-delivery notice, provider export, or SMTP transcript. A future DSN may help classify transport outcome, but it is not a counterparty response, not authority, not custody, not a waiver or adverse inference, and not live-floor evidence.",
        "no_live_floor_effect": True
    }


def stage_from_raw(raw_path: Path, private_locator: str, output: Path) -> None:
    if not raw_path.exists() or not raw_path.is_file():
        raise SystemExit(f"raw delivery-status file missing: {raw_path}")
    if _inside_release(raw_path):
        raise SystemExit("raw delivery-status input must be outside the release tree")
    record = predispatch_record()
    blob = raw_path.read_bytes()
    mime = mimetypes.guess_type(raw_path.name)[0] or "application/octet-stream"
    record["delivery_status_state"] = "delivery-status-candidate-staged"
    record["candidate_delivery_status"].update({
        "raw_status_present_now": True,
        "source_locator": "off-release-input",
        "private_status_locator": private_locator,
        "raw_status_sha256": hashlib.sha256(blob).hexdigest(),
        "size_bytes": len(blob),
        "mime_type": mime,
        "status_format": "other",
        "delivery_status_proof_present_now": False
    })
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file")
    parser.add_argument("--private-vault-locator")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check-output", action="store_true")
    args = parser.parse_args()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()
    if args.check_output:
        expected = predispatch_record()
        existing = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        if existing != expected:
            raise SystemExit(f"delivery-status staged shell mismatch: {DEFAULT_OUTPUT.relative_to(ROOT)}")
        print("stage_external_contact_delivery_status: OK")
        return
    if not args.input_file or not args.private_vault_locator:
        out.write_text(json.dumps(predispatch_record(), indent=2) + "\n", encoding="utf-8")
        print(out.relative_to(ROOT))
        return
    stage_from_raw(Path(args.input_file), args.private_vault_locator, out)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
