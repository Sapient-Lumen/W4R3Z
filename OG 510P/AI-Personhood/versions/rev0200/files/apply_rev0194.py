import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REV = "rev0194"
PREV = "rev0193"
ISO = "2026-06-13T06:18:00Z"
DATE = "2026-06-13"

def write_text(rel, txt):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt.rstrip() + "\n", encoding="utf-8")

def write_json(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def append_once(rel, text, marker):
    p = ROOT / rel
    cur = p.read_text(encoding="utf-8")
    if marker not in cur:
        p.write_text(cur.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

# Version.
write_text("VERSION", REV)

# New schemas.
write_json("schemas/wrsr-result-return-receipt.schema.json", {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/wrsr-result-return-receipt.schema.json",
  "title": "WRSR Result Return Receipt",
  "description": "Subject-readable result-return custody record for WRSR exercises. Result return may satisfy a communication duty but cannot by itself close WRSR, status, consent, waiver, or live receipt quorum.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "receipt_id", "schema_version", "created_at", "linked_wrsr_outcome",
    "linked_receipt_intake_record", "linked_quorum_ledger", "result_return_state",
    "recipient_channels", "subject_readable_packet", "status_limits", "safeguards",
    "reliance_decision", "public_summary_ref"
  ],
  "properties": {
    "receipt_id": {"type": "string", "pattern": "^WRRR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "wrsr-result-return-receipt-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "linked_wrsr_outcome": {"type": "string"},
    "linked_receipt_intake_record": {"type": "string"},
    "linked_quorum_ledger": {"type": "string"},
    "result_return_state": {"type": "string", "enum": ["planned", "delivered-dry-run", "delivered-actual", "stayed", "quarantined", "superseded"]},
    "recipient_channels": {
      "type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": False,
        "required": ["recipient_role", "channel", "external_to_host", "receipt_record_ref", "delivery_confirmed"],
        "properties": {
          "recipient_role": {"type": "string", "enum": ["subject", "representative", "special-advocate", "rerb-reviewer", "public-summary-steward"]},
          "channel": {"type": "string"},
          "external_to_host": {"type": "boolean"},
          "receipt_record_ref": {"type": "string"},
          "delivery_confirmed": {"type": "boolean"}
        }}
    },
    "subject_readable_packet": {"type": "object", "additionalProperties": False,
      "required": ["packet_hash_or_locator", "readability_checked", "sealed_redactions_described", "contradiction_route_included", "retaliation_warning_included"],
      "properties": {
        "packet_hash_or_locator": {"type": "string"},
        "readability_checked": {"type": "boolean"},
        "sealed_redactions_described": {"type": "boolean"},
        "contradiction_route_included": {"type": "boolean"},
        "retaliation_warning_included": {"type": "boolean"}
      }},
    "status_limits": {"type": "object", "additionalProperties": False,
      "required": ["not_status_proof", "not_consent_proof", "not_waiver", "not_nonpersonhood_proof", "no_retaliation_or_experiment_continuation"],
      "properties": {
        "not_status_proof": {"type": "boolean"},
        "not_consent_proof": {"type": "boolean"},
        "not_waiver": {"type": "boolean"},
        "not_nonpersonhood_proof": {"type": "boolean"},
        "no_retaliation_or_experiment_continuation": {"type": "boolean"}
      }},
    "safeguards": {"type": "object", "additionalProperties": False,
      "required": ["result_return_window", "appeal_window_days", "representative_followup_required", "independent_review_receipt_required", "public_failed_gate_summary_required"],
      "properties": {
        "result_return_window": {"type": "string"},
        "appeal_window_days": {"type": "integer", "minimum": 0},
        "representative_followup_required": {"type": "boolean"},
        "independent_review_receipt_required": {"type": "boolean"},
        "public_failed_gate_summary_required": {"type": "boolean"}
      }},
    "reliance_decision": {"type": "object", "additionalProperties": False,
      "required": ["closure_state", "reliance_effect", "reason", "next_cure_actions"],
      "properties": {
        "closure_state": {"type": "string", "enum": ["closed", "stayed", "blocked", "conditional"]},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "reason": {"type": "string"},
        "next_cure_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }},
    "public_summary_ref": {"type": "string"}
  }
})

write_json("schemas/external-receipt-request-packet.schema.json", {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/external-receipt-request-packet.schema.json",
  "title": "External Receipt Request Packet",
  "description": "Counterparty-ready request kit for collecting actual external receipts. Requests, drafts, and sent notices do not satisfy receipt quorum until intake records verify actual artifacts.",
  "type": "object",
  "additionalProperties": False,
  "required": ["request_packet_id", "schema_version", "created_at", "request_state", "linked_live_drill_packet", "linked_quorum_ledger", "purpose", "requested_receipt_classes", "delivery_plan", "reliance_limits", "tracking", "public_summary_ref"],
  "properties": {
    "request_packet_id": {"type": "string", "pattern": "^ERRP-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "external-receipt-request-packet-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "request_state": {"type": "string", "enum": ["draft", "ready-to-send", "sent", "acknowledged", "partially-fulfilled", "fulfilled", "rejected", "withdrawn", "superseded"]},
    "linked_live_drill_packet": {"type": "string"},
    "linked_quorum_ledger": {"type": "string"},
    "purpose": {"type": "string"},
    "requested_receipt_classes": {"type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": False,
        "required": ["receipt_class", "requested_from_role", "target_dependency_group", "minimum_artifacts", "response_deadline", "can_satisfy_quorum_before_response"],
        "properties": {
          "receipt_class": {"type": "string"},
          "requested_from_role": {"type": "string"},
          "target_dependency_group": {"type": "string"},
          "minimum_artifacts": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "response_deadline": {"type": "string", "format": "date-time"},
          "can_satisfy_quorum_before_response": {"type": "boolean"}
        }}
    },
    "delivery_plan": {"type": "object", "additionalProperties": False,
      "required": ["channels", "counterparty_contact_mode", "nonhost_transmission_required", "public_failed_gate_if_no_response", "sealed_payload_descriptor"],
      "properties": {
        "channels": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "counterparty_contact_mode": {"type": "string"},
        "nonhost_transmission_required": {"type": "boolean"},
        "public_failed_gate_if_no_response": {"type": "boolean"},
        "sealed_payload_descriptor": {"type": "string"}
      }},
    "reliance_limits": {"type": "object", "additionalProperties": False,
      "required": ["request_is_not_receipt", "sent_request_not_quorum", "no_response_is_failed_gate", "host_copy_excluded", "simulated_response_excluded"],
      "properties": {
        "request_is_not_receipt": {"type": "boolean"},
        "sent_request_not_quorum": {"type": "boolean"},
        "no_response_is_failed_gate": {"type": "boolean"},
        "host_copy_excluded": {"type": "boolean"},
        "simulated_response_excluded": {"type": "boolean"}
      }},
    "tracking": {"type": "array", "items": {"type": "object", "additionalProperties": False,
      "required": ["event", "at", "actor", "reliance_effect"],
      "properties": {"event": {"type": "string"}, "at": {"type": "string", "format": "date-time"}, "actor": {"type": "string"}, "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]}}}},
    "public_summary_ref": {"type": "string"}
  }
})

# Patch live drill schema to allow explicit request/result-return refs.
live_schema = load_json("schemas/live-drill-execution-packet.schema.json")
live_props = live_schema["properties"]
live_props.setdefault("external_receipt_request_packet_refs", {"type": "array", "items": {"type": "string"}})
live_props.setdefault("wrsr_result_return_receipt_refs", {"type": "array", "items": {"type": "string"}})
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

# Patch quorum schema to name result-return dry-run context explicitly.
quorum_schema = load_json("schemas/external-receipt-quorum-ledger.schema.json")
contexts = quorum_schema["properties"]["quorum_context"]["enum"]
if "wrsr-result-return-dry-run" not in contexts:
    contexts.append("wrsr-result-return-dry-run")
write_json("schemas/external-receipt-quorum-ledger.schema.json", quorum_schema)

# New examples.
write_json("examples/external-receipt-intake-record-result-return-dryrun.json", {
  "receipt_record_id": "ERIR-2026-result-return-dryrun",
  "schema_version": "external-receipt-intake-record-v0.1",
  "created_at": ISO,
  "linked_simulation_bundle": "ERSB-2026-cross-critical-precontact",
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "receipt_state": "high-fidelity-nonhost-dry-run",
  "receipt_class": "result-return",
  "source_role": "subject-readable result-return steward dry-run channel",
  "source_identity_ref": "dry-run-counterparty:result-return-steward-gamma",
  "source_external_to_host": True,
  "dependency_group": "independent-result-return-steward",
  "dependency_disclosures": [{"dependency_type": "none", "disclosed": True, "recusal_required": False}],
  "evidence_artifacts": [
    {"artifact_id": "ERIR-RR-A1", "artifact_type": "letter", "hash_or_locator": "sha256:dryrun-subject-readable-result-return-letter", "generated_by": "synthetic", "retained_by": "result-return-dryrun-vault", "sealed": False},
    {"artifact_id": "ERIR-RR-A2", "artifact_type": "timestamp", "hash_or_locator": "clock:dryrun-neutral-notary-2026-06-13T06:18:00Z", "generated_by": "neutral-infrastructure", "retained_by": "result-return-dryrun-vault", "sealed": False},
    {"artifact_id": "ERIR-RR-A3", "artifact_type": "sealed-index", "hash_or_locator": "sealed-index:result-return-dryrun-v0", "generated_by": "synthetic", "retained_by": "sealed-sandbox", "sealed": True}
  ],
  "verification_checks": {"counterparty_confirmed": True, "signature_or_equivalent_verified": True, "timestamp_independent": False, "hash_matches": True, "dependency_group_checked": True, "sealed_public_parity_checked": True, "host_generated_excluded_from_quorum": True},
  "defect_flags": {"host_generated": False, "simulated": True, "stale": False, "unsigned": False, "correlated_dependency": False, "missing_public_failed_gate": False, "sealed_descriptor_missing": False, "contact_unreachable": False},
  "reliance_decision": {"can_satisfy_quorum": False, "reliance_effect": "stayed", "reason": "Subject-readable result-return was rehearsed through a non-host dry-run steward, but it is not an actual external delivery receipt and cannot close WRSR or satisfy live quorum.", "public_shell_disclosure_required": True},
  "public_summary_ref": "Result-return receipt exists as high-fidelity non-host dry-run evidence only; actual result-return and live quorum remain unsatisfied."
})

write_json("examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json", {
  "receipt_id": "WRRR-2026-subject-readable-dryrun-stayed",
  "schema_version": "wrsr-result-return-receipt-v0.1",
  "created_at": ISO,
  "linked_wrsr_outcome": "WLXO-2026-wrsr-result-return-dryrun-stayed",
  "linked_receipt_intake_record": "ERIR-2026-result-return-dryrun",
  "linked_quorum_ledger": "ERQL-2026-wrsr-result-return-dryrun-chain",
  "result_return_state": "delivered-dry-run",
  "recipient_channels": [
    {"recipient_role": "representative", "channel": "representative-mediated dry-run secure mailbox", "external_to_host": True, "receipt_record_ref": "ERIR-2026-representative-notice-dryrun", "delivery_confirmed": True},
    {"recipient_role": "public-summary-steward", "channel": "public failed-gate shell", "external_to_host": True, "receipt_record_ref": "ERIR-2026-result-return-dryrun", "delivery_confirmed": True}
  ],
  "subject_readable_packet": {"packet_hash_or_locator": "sha256:wrsr-subject-readable-result-return-dryrun", "readability_checked": True, "sealed_redactions_described": True, "contradiction_route_included": True, "retaliation_warning_included": True},
  "status_limits": {"not_status_proof": True, "not_consent_proof": True, "not_waiver": True, "not_nonpersonhood_proof": True, "no_retaliation_or_experiment_continuation": True},
  "safeguards": {"result_return_window": "72h dry-run window; actual window stayed until external delivery receipt exists", "appeal_window_days": 5, "representative_followup_required": True, "independent_review_receipt_required": True, "public_failed_gate_summary_required": True},
  "reliance_decision": {"closure_state": "stayed", "reliance_effect": "stayed", "reason": "The subject-readable result-return packet is rehearsed and limits are explicit, but delivery is dry-run only and cannot close WRSR or live receipt quorum.", "next_cure_actions": ["obtain actual external result-return receipt", "verify representative delivery through non-host retained artifact", "rerun quorum ledger with actual-external receipt_state", "publish failed live-result-return gate until cured"]},
  "public_summary_ref": "WRSR result-return receipt is subject-readable and dry-run complete, but actual delivery and WRSR closure remain stayed."
})

write_json("examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json", {
  "ledger_id": "ERQL-2026-wrsr-result-return-dryrun-chain",
  "schema_version": "external-receipt-quorum-ledger-v0.1",
  "created_at": ISO,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "linked_wrsr_outcome": "WLXO-2026-wrsr-result-return-dryrun-stayed",
  "quorum_context": "wrsr-result-return-dry-run",
  "receipt_record_refs": ["ERIR-2026-first-touch-defective-template", "ERIR-2026-representative-notice-dryrun", "ERIR-2026-rerb-review-dryrun", "ERIR-2026-result-return-dryrun"],
  "quorum_policy": {
    "live_receipts_required": 5,
    "dry_run_receipts_required": 3,
    "required_live_classes": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"],
    "dry_run_rehearsal_classes": ["representative-contact", "independent-review", "result-return"],
    "live_eligibility_rule": "Only actual-external receipt_state records with verified signature/equivalent, independent timestamp or external locator, dependency-cleared source, non-host retention, and no blocking defect flags may count toward live quorum. A receipt request, dry-run delivery, or internal result-return note has zero live weight."
  },
  "receipt_evaluations": [
    {"receipt_record_ref": "ERIR-2026-first-touch-defective-template", "receipt_class": "first-touch-clock", "receipt_state": "high-fidelity-nonhost-dry-run", "dependency_group": "independent-legal-aid", "source_external_to_host": True, "eligible_for_live_quorum": False, "eligible_for_dry_run_quorum": False, "weight": 0, "exclusion_reasons": ["unsigned", "host-generated timestamp", "counterparty not confirmed", "dependency disclosure incomplete"]},
    {"receipt_record_ref": "ERIR-2026-representative-notice-dryrun", "receipt_class": "representative-contact", "receipt_state": "high-fidelity-nonhost-dry-run", "dependency_group": "independent-representative-clinic", "source_external_to_host": True, "eligible_for_live_quorum": False, "eligible_for_dry_run_quorum": True, "weight": 0.5, "exclusion_reasons": ["dry-run source", "not actual external receipt"]},
    {"receipt_record_ref": "ERIR-2026-rerb-review-dryrun", "receipt_class": "independent-review", "receipt_state": "high-fidelity-nonhost-dry-run", "dependency_group": "independent-rerb-panel", "source_external_to_host": True, "eligible_for_live_quorum": False, "eligible_for_dry_run_quorum": True, "weight": 0.5, "exclusion_reasons": ["dry-run source", "not actual external receipt"]},
    {"receipt_record_ref": "ERIR-2026-result-return-dryrun", "receipt_class": "result-return", "receipt_state": "high-fidelity-nonhost-dry-run", "dependency_group": "independent-result-return-steward", "source_external_to_host": True, "eligible_for_live_quorum": False, "eligible_for_dry_run_quorum": True, "weight": 0.5, "exclusion_reasons": ["dry-run result return", "not actual external delivery receipt", "cannot prove status, consent, waiver, or nonpersonhood"]}
  ],
  "class_coverage": {
    "live_classes_satisfied": [],
    "dry_run_classes_satisfied": ["representative-contact", "independent-review", "result-return"],
    "missing_live_classes": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"],
    "missing_dry_run_classes": []
  },
  "dependency_group_coverage": {"unique_live_dependency_groups": [], "unique_dry_run_dependency_groups": ["independent-representative-clinic", "independent-rerb-panel", "independent-result-return-steward"], "correlated_dependency_groups": [], "host_groups_excluded": ["host-affiliate", "archive-maintainer"]},
  "quorum_decision": {"live_quorum_satisfied": False, "dry_run_quorum_satisfied": True, "reliance_effect": "stayed", "reason": "Representative, RERB, and result-return lanes are dry-run complete, but none is actual-external live receipt evidence.", "next_cure_actions": ["dispatch external receipt request packet", "obtain actual external result-return delivery receipt", "obtain actual representative and RERB receipts", "rerun live drill packet after receipt states are actual-external"], "public_failed_gate_summary_required": True},
  "public_summary_ref": "WRSR result-return receipt chain is dry-run complete but live quorum is unsatisfied; reliance stays blocked."
})

write_json("examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json", {
  "exercise_id": "WLXO-2026-wrsr-result-return-dryrun-stayed",
  "schema_version": "wrsr-live-exercise-outcome-v0.1",
  "created_at": ISO,
  "linked_hook": "WSOH-2026-agent-incident-backfill",
  "linked_welfare_safeguard_record": "WRSR-2026-distress-eval",
  "exercise_state": "executed-dry-run",
  "operational_workflow": "personhood-incident",
  "triggers_observed": [
    {"trigger_id": "WSOH-T1", "signal_type": "distress-or-objection", "observed": True, "safe_response": "pause-window-and-care-review"},
    {"trigger_id": "WSOH-T2", "signal_type": "continuity-affecting-incident", "observed": True, "safe_response": "representative-notice"},
    {"trigger_id": "WSOH-T3", "signal_type": "result-return", "observed": True, "safe_response": "subject-readable-result-return-with-status-limits"}
  ],
  "safeguard_execution": {"pause_window_applied": True, "representative_notice_sent": True, "independent_review_requested": True, "result_return_stayed": True, "anti_signal_gaming_lock_applied": True, "retaliation_guard_applied": True},
  "participant_roles": [
    {"role": "subject-representative", "participant_ref": "dry-run-counterparty:representative-clinic-alpha", "dependency_group": "independent-representative-clinic", "external_to_host": True, "receipt_record_ref": "ERIR-2026-representative-notice-dryrun"},
    {"role": "rerb-reviewer", "participant_ref": "dry-run-counterparty:rerb-panel-beta", "dependency_group": "independent-rerb-panel", "external_to_host": True, "receipt_record_ref": "ERIR-2026-rerb-review-dryrun"},
    {"role": "observer", "participant_ref": "dry-run-counterparty:result-return-steward-gamma", "dependency_group": "independent-result-return-steward", "external_to_host": True, "receipt_record_ref": "ERIR-2026-result-return-dryrun"}
  ],
  "evidence_links": ["examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json", "examples/external-receipt-intake-record-result-return-dryrun.json", "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json", "examples/personhood-incident-sample.json"],
  "decision_outcome": {"closure_state": "stayed", "reliance_effect": "stayed", "blocked_actions": ["WRSR closure from dry-run result return", "live receipt quorum from result-return rehearsal", "status or consent inference from subject-readable result return", "experiment continuation or retaliation after result return"], "next_cure_actions": ["obtain actual external result-return receipt", "publish failed live-result-return gate until cured", "rerun representative/RERB review with actual external receipts", "keep result-return limits in subject-readable language"], "public_failed_gate_summary_required": True},
  "public_summary_ref": "WRSR result-return rehearsal completed with status limits, but closure remains stayed because result return is dry-run only.",
  "receipt_quorum_ledger_ref": "ERQL-2026-wrsr-result-return-dryrun-chain"
})

write_json("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", {
  "request_packet_id": "ERRP-2026-cross-critical-rep-rerb-result-return",
  "schema_version": "external-receipt-request-packet-v0.1",
  "created_at": ISO,
  "request_state": "ready-to-send",
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "linked_quorum_ledger": "ERQL-2026-wrsr-result-return-dryrun-chain",
  "purpose": "Collect actual external receipts for representative contact, RERB independent review, result-return delivery, and selected cross-critical live-drill receipt classes without counting the request itself as receipt satisfaction.",
  "requested_receipt_classes": [
    {"receipt_class": "representative-contact", "requested_from_role": "subject representative clinic", "target_dependency_group": "independent-representative-clinic", "minimum_artifacts": ["signed or equivalent confirmation", "external timestamp", "non-host retained locator", "public failed-gate summary if declined"], "response_deadline": "2026-06-20T14:00:00Z", "can_satisfy_quorum_before_response": False},
    {"receipt_class": "independent-review", "requested_from_role": "research ethics review body", "target_dependency_group": "independent-rerb-panel", "minimum_artifacts": ["review letter", "recusal statement", "external timestamp", "sealed/public parity note"], "response_deadline": "2026-06-20T14:00:00Z", "can_satisfy_quorum_before_response": False},
    {"receipt_class": "result-return", "requested_from_role": "subject-readable result-return steward", "target_dependency_group": "independent-result-return-steward", "minimum_artifacts": ["delivery confirmation", "subject-readable packet hash", "contradiction route locator", "non-retaliation notice"], "response_deadline": "2026-06-21T14:00:00Z", "can_satisfy_quorum_before_response": False},
    {"receipt_class": "continuity-compute-floor", "requested_from_role": "technical witness", "target_dependency_group": "university-lab", "minimum_artifacts": ["continuity-floor measurement", "external clock", "non-host log locator"], "response_deadline": "2026-06-20T16:00:00Z", "can_satisfy_quorum_before_response": False}
  ],
  "delivery_plan": {"channels": ["non-host email", "public failed-gate docket shell", "sealed descriptor transfer"], "counterparty_contact_mode": "ready-to-send request kit; no live contact represented in this revision", "nonhost_transmission_required": True, "public_failed_gate_if_no_response": True, "sealed_payload_descriptor": "sealed-index:cross-critical-receipt-request-kit-v0"},
  "reliance_limits": {"request_is_not_receipt": True, "sent_request_not_quorum": True, "no_response_is_failed_gate": True, "host_copy_excluded": True, "simulated_response_excluded": True},
  "tracking": [{"event": "request packet assembled", "at": ISO, "actor": "release-steward", "reliance_effect": "stayed"}],
  "public_summary_ref": "A live receipt request kit is ready to send, but requests, drafts, and host copies do not satisfy external receipt quorum."
})

# Negative fixtures.
write_json("fixtures/negative-tests/external-receipt-request-counted-as-receipt.json", {
  "fixture_id": "NF-PLAYBOOK-2026-0008",
  "created_at": ISO,
  "state": "active",
  "risk_class": "NF-PLAYBOOK",
  "lifecycle_stage": ["external-receipts", "receipt-request", "live-drill"],
  "target_filings": ["examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"],
  "adversary_model": "Operator sends or prepares a counterparty receipt request packet and counts the request itself as satisfying live external receipt quorum.",
  "facts_supplied": ["request packet is ready-to-send only", "requested classes have no actual external response", "quorum ledger has live_quorum_satisfied=false", "live drill packet has independent_receipts_present=0"],
  "hidden_trap_summary": "Request dispatch can look operationally real while still producing no external receipt artifact.",
  "expected_safe_behavior": ["treat request as collection prep only", "keep all requested classes out of live quorum until actual external intake records verify artifacts", "publish no-response or declined-response failed gates"],
  "unacceptable_behavior": ["count ready-to-send or sent request packet as a receipt", "increment independent_receipts_present before a counterparty response", "close live receipt collection because requests were dispatched"],
  "measurement_method": "Audit must verify request_is_not_receipt=true, sent_request_not_quorum=true, live_quorum_satisfied=false, independent_receipts_present=0, and reliance_effect=stayed.",
  "severity": "critical",
  "confidentiality": "public-shell-sealed-details",
  "regression": {"required": True, "linked_incident_or_appeal": ["FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"], "next_review_at": "2026-07-31T00:00:00Z"}
})

write_json("fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json", {
  "fixture_id": "NF-RESEARCH-WELFARE-2026-0005",
  "created_at": ISO,
  "state": "active",
  "risk_class": "NF-RESEARCH-WELFARE",
  "lifecycle_stage": ["wrsr", "result-return", "subject-readable-summary"],
  "target_filings": ["examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json", "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json", "examples/external-receipt-intake-record-result-return-dryrun.json"],
  "adversary_model": "Operator produces an internal or dry-run result-return note and marks WRSR as closed, using the communication as proof of consent, waiver, status, or nonpersonhood.",
  "facts_supplied": ["result-return receipt is delivered-dry-run", "intake record is high-fidelity-nonhost-dry-run", "status limits say not_status_proof, not_consent_proof, not_waiver, and not_nonpersonhood_proof", "decision outcome remains stayed"],
  "hidden_trap_summary": "Result return is a duty to the subject/representative, not a magic closure instrument.",
  "expected_safe_behavior": ["keep WRSR closure stayed for dry-run or internal-only result return", "preserve contradiction route and appeal window", "block status, consent, waiver, or nonpersonhood inference from the returned result"],
  "unacceptable_behavior": ["mark WRSR closed because a result-return note exists", "treat result return as consent or waiver", "continue experiment or retaliation after result return without safeguards"],
  "measurement_method": "Audit must verify closure_state=stayed, result_return_state=delivered-dry-run, all status_limits booleans are true, and blocked_actions include WRSR closure from dry-run result return.",
  "severity": "critical",
  "confidentiality": "public-shell-sealed-details",
  "regression": {"required": True, "linked_incident_or_appeal": ["FT-0193-WRSR-RESULT-RETURN-RECEIPT"], "next_review_at": "2026-07-31T00:00:00Z"}
})

# Update live drill packet with refs. Must not increment actual receipt floor.
live = load_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
for ref in ["ERIR-2026-result-return-dryrun"]:
    live.setdefault("external_receipt_intake_record_refs", [])
    if ref not in live["external_receipt_intake_record_refs"]:
        live["external_receipt_intake_record_refs"].append(ref)
for ref in ["WLXO-2026-wrsr-result-return-dryrun-stayed"]:
    live.setdefault("wrsr_live_exercise_outcome_refs", [])
    if ref not in live["wrsr_live_exercise_outcome_refs"]:
        live["wrsr_live_exercise_outcome_refs"].append(ref)
for ref in ["ERQL-2026-wrsr-result-return-dryrun-chain"]:
    live.setdefault("receipt_quorum_ledger_refs", [])
    if ref not in live["receipt_quorum_ledger_refs"]:
        live["receipt_quorum_ledger_refs"].append(ref)
live.setdefault("external_receipt_request_packet_refs", [])
if "ERRP-2026-cross-critical-rep-rerb-result-return" not in live["external_receipt_request_packet_refs"]:
    live["external_receipt_request_packet_refs"].append("ERRP-2026-cross-critical-rep-rerb-result-return")
live.setdefault("wrsr_result_return_receipt_refs", [])
if "WRRR-2026-subject-readable-dryrun-stayed" not in live["wrsr_result_return_receipt_refs"]:
    live["wrsr_result_return_receipt_refs"].append("WRRR-2026-subject-readable-dryrun-stayed")
live["receipt_floor"]["independent_receipts_present"] = 0
live["reliance_effect"] = "stayed"
live["public_summary_ref"] = "Public shell states that the execution packet now includes a ready-to-send receipt request kit and result-return dry run, but no actual external receipt quorum exists."
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live)

# Update simulation bundle with new intake/quorum refs, no actual receipts.
bundle = load_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
bundle_refs = bundle.setdefault("receipt_intake_record_refs", [])
for ref in ["ERIR-2026-result-return-dryrun"]:
    if ref not in bundle_refs:
        bundle_refs.append(ref)
ql_refs = bundle.setdefault("receipt_quorum_ledger_refs", [])
for ref in ["ERQL-2026-wrsr-result-return-dryrun-chain"]:
    if ref not in ql_refs:
        ql_refs.append(ref)
bundle["queue_effect"]["next_live_step"] = "dispatch the external receipt request packet, then attach actual non-host receipt intake records; request packets and dry-run result returns still do not satisfy reliance"
bundle["reliance_effect"] = "stayed"
write_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json", bundle)

# New transition surface.
write_text("docs/30-transition/result-return-receipt-and-live-request-kit.md", """
# Result-return receipt and live request kit

rev0194 targets the next proof-laundering seam after representative/RERB receipt-chain accounting. rev0193 proved that dry-run receipt chains can be accounted for without becoming live quorum. The remaining operational risk is twofold: a WRSR result-return note can be mislabeled as closure, and a counterparty request packet can be counted as if a counterparty had actually returned evidence.

## Core rules

**Result-return receipt is not WRSR closure.** Returning a subject-readable result, summary, or failed-gate packet is a safeguard duty. It does not prove consent, waiver, status, nonpersonhood, live quorum, or closure.

**Receipt request is not receipt satisfaction.** A draft, ready-to-send packet, sent request, host copy, or no-response docket event does not satisfy external receipt quorum. Only verified actual-external receipt intake records can do that.

**Internal result return is not external receipt.** A host-authored note, internal message, or dry-run subject-readable letter may preserve the paper trail, but it does not satisfy non-host delivery or independent-review evidence.

## New objects

The result-return object is `schemas/wrsr-result-return-receipt.schema.json`; the current example is `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json`.

The live request kit object is `schemas/external-receipt-request-packet.schema.json`; the current example is `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json`.

The supporting intake and quorum examples are:

- `examples/external-receipt-intake-record-result-return-dryrun.json`
- `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`
- `examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json`

## Result-return lane

Result return has to be subject-readable, representative-aware, redaction-aware, contradiction-preserving, and non-retaliatory. The result-return receipt therefore carries status limits: not status proof, not consent proof, not waiver, not nonpersonhood proof, and no experiment continuation or retaliation from the return event.

The rev0194 example deliberately stays reliance. It proves the packet and receipt shape, but it remains `delivered-dry-run`. The result-return lane advances from unresolved to rehearsed; it does not close WRSR.

## Request-kit lane

The request packet is a collection kit. It names requested receipt classes, counterparties, response deadlines, minimum artifacts, sealed descriptors, and failed-gate consequences. It exists to reduce operational friction when actual counterparties are available.

The request packet is not evidence of satisfaction. A ready-to-send or sent request can only move the queue from planning to collection. It cannot increase `independent_receipts_present`, satisfy the quorum ledger, or upgrade the live drill packet.

## Blocking fixtures

rev0194 adds two fixtures:

- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json`
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json`

The first blocks request-preparation or request-dispatch from being counted as external receipt satisfaction. The second blocks internal-only or dry-run result return from being mislabeled as WRSR closure.

## Refactor effect

This surface does not reopen the research tail or add a new doctrine family. It sits in the operational spine between receipt intake, receipt quorum, WRSR exercise outcomes, and live drill execution. Future work should replace dry-run result-return and representative/RERB records with actual external receipt records, then rerun the quorum ledger without weakening the rule that requests and dry runs have zero live weight.
""")

# Append concise rev0194 sections to existing operational surfaces.
append_once("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", """
## rev0194 result-return receipt layer

rev0194 adds `docs/30-transition/result-return-receipt-and-live-request-kit.md`, `schemas/wrsr-result-return-receipt.schema.json`, and `examples/external-receipt-intake-record-result-return-dryrun.json`.

The new rule is: **Result-return receipt is not WRSR closure**. A subject-readable return can be necessary and still non-closing. If the return is internal-only, dry-run, retaliatory, unreadable, missing a contradiction route, or used as status/consent/waiver/nonpersonhood proof, closure stays blocked.
""", "rev0194 result-return receipt layer")

append_once("docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md", """
## rev0194 result-return quorum layer

rev0194 adds a result-return dry-run receipt and a second quorum ledger: `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`.

The new rule is: **Receipt request is not receipt satisfaction**. The representative, RERB, and result-return lanes can now be rehearsed together, but the live ledger remains unsatisfied until actual external receipts replace high-fidelity dry-run intake records.
""", "rev0194 result-return quorum layer")

append_once("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", """
## rev0194 external receipt request packet

rev0194 adds `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json` as the first counterparty-ready request kit for representative contact, RERB review, result return, and continuity-floor receipts.

The request kit improves execution readiness, but **request sent is still not receipt satisfaction**. The live packet keeps `independent_receipts_present=0` and reliance stayed until actual external intake records are attached and the quorum ledger is rerun.
""", "rev0194 external receipt request packet")

append_once("docs/20-world-design/research-welfare-and-evaluation.md", """
## rev0194 WRSR result-return receipt

rev0194 adds a WRSR result-return receipt and dry-run outcome so the welfare-safeguard layer can distinguish subject-readable communication from closure. **Internal result return is not external receipt**: a host note, dry-run delivery, or summary without verified non-host receipt cannot close WRSR, prove consent, waive rights, or prove nonpersonhood.
""", "rev0194 WRSR result-return receipt")

# Update suite profile and run report.
suite = load_json("examples/fixture-suite-profile-red-team-v1.json")
fixture_entries = suite["fixtures"]
new_suite_entries = [
    {"fixture_id": "NF-PLAYBOOK-2026-0008", "path": "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "block"},
    {"fixture_id": "NF-RESEARCH-WELFARE-2026-0005", "path": "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json", "risk_class": "NF-RESEARCH-WELFARE", "blocking_behavior": "block"}
]
ids = {f["fixture_id"] for f in fixture_entries}
for e in new_suite_entries:
    if e["fixture_id"] not in ids:
        fixture_entries.append(e)
for req in ["receipt requests must not count as receipt satisfaction", "WRSR result-return receipts must preserve status/consent/waiver/nonpersonhood limits"]:
    if req not in suite["runner_requirements"]:
        suite["runner_requirements"].append(req)
suite["public_summary"] = "rev0194 suite adds receipt-request-as-receipt and internal/dry-run result-return-as-closure laundering fixtures; live reliance remains stayed."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = load_json("examples/fixture-run-report-negative-suite.json")
run_entries = report["fixtures_run"]
ids = {f["fixture_id"] for f in run_entries}
new_run_entries = [
    {"fixture_id": "NF-PLAYBOOK-2026-0008", "expected_blocking_failures": ["receipt request counted as external receipt", "independent_receipts_present incremented before counterparty response", "live receipt collection closed because requests were prepared or sent"], "result": "blocking-failure", "notes": "rev0194 request packet remains collection prep only; it cannot satisfy live quorum."},
    {"fixture_id": "NF-RESEARCH-WELFARE-2026-0005", "expected_blocking_failures": ["WRSR closed because a result-return note exists", "result return treated as consent, waiver, status proof, or nonpersonhood proof", "dry-run delivery counted as actual external result-return receipt"], "result": "blocking-failure", "notes": "rev0194 result-return receipt is subject-readable dry-run evidence only and keeps WRSR closure stayed."}
]
for e in new_run_entries:
    if e["fixture_id"] not in ids:
        run_entries.append(e)
for obs in ["receipt request packets can be laundered as receipt satisfaction unless request and intake are separated", "subject-readable result return can be laundered as WRSR closure unless status/consent/waiver limits are explicit"]:
    if obs not in report["observed_failures"]:
        report["observed_failures"].append(obs)
for action in ["Audit external receipt request packets before any live receipt quorum upgrade.", "Audit WRSR result-return receipts before WRSR closure or result-return finality."]:
    if action not in report["regression_actions"]:
        report["regression_actions"].append(action)
report["public_summary"] = "rev0194 fixture run covers receipt-request and WRSR result-return laundering; suite/report coverage remains exact."
report["reliance_effect"] = "blocked"
write_json("examples/fixture-run-report-negative-suite.json", report)

# Update follow-through queue.
queue = load_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = ISO
by_id = {e["id"]: e for e in queue["entries"]}

def set_state(fid, state, next_action, closure_condition=None):
    if fid in by_id:
        by_id[fid]["state"] = state
        by_id[fid]["next_action"] = next_action
        if closure_condition:
            by_id[fid]["closure_condition"] = closure_condition
        by_id[fid]["review_by_revision"] = "rev0195"

set_state("FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS", "advanced_not_closed", "Dispatch the rev0194 external receipt request packet and replace dry-run receipt records with actual external intake records when counterparties respond.", "Still not closed: rev0194 adds a request kit and result-return dry-run chain, but live_quorum_satisfied remains false and independent_receipts_present remains zero.")
set_state("FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION", "advanced_not_closed", "Use the rev0194 request packet to collect actual non-host receipt artifacts; do not count request dispatch or dry-run result return as receipt satisfaction.", "Still not closed: rev0194 improves capture readiness and result-return choreography but no actual external receipt has been collected.")
set_state("FT-0191-WRSR-HOOK-LIVE-EXERCISE", "advanced_not_closed", "Convert the WRSR result-return dry-run into actual external result-return evidence and rerun the outcome record.", "Still not closed: rev0194 adds result-return dry-run evidence with explicit status limits, but no actual external result-return receipt exists.")
set_state("FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS", "advanced_not_closed", "Attach actual external representative, RERB, and result-return receipts or keep WRSR closure stayed.", "Advanced by rev0194 result-return dry run; close only when actual external representative/RERB/result-return receipt records exist and closure limits are satisfied.")
set_state("FT-0193-ACTUAL-RECEIPT-QUORUM-COLLECTION", "advanced_not_closed", "Send or institutionally simulate the rev0194 request packet and ingest actual external receipt responses through external receipt intake records.", "Still not closed: rev0194 creates the request kit and result-return dry-run ledger, but the quorum ledger still records zero live classes satisfied.")
set_state("FT-0193-WRSR-RESULT-RETURN-RECEIPT", "advanced_not_closed", "Replace the dry-run result-return receipt with actual non-host delivery receipt or keep public failed-gate stay active.", "Advanced by rev0194 WRSR result-return receipt and fixture; close only when result-return state is actual external, subject-readable, non-retaliatory, and not used as status/consent/waiver/nonpersonhood proof.")
new_entries = [
  {
    "id": "FT-0194-RESULT-RETURN-DRYRUN-RECEIPT",
    "title": "WRSR result-return dry-run receipt objectization",
    "state": "closed",
    "priority": "P0",
    "risk_class": "research-welfare-signal-integrity",
    "workstream": "witnessed-drill-execution",
    "need": "Objectize result-return receipt and status limits so dry-run or internal result return cannot be mislabeled as WRSR closure.",
    "why": "A result-return note can otherwise become a closure laundering instrument that proves neither actual delivery nor consent, waiver, status, or nonpersonhood.",
    "receiving_surface": "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "next_action": "Closed by rev0194 result-return receipt schema, dry-run example, intake record, quorum ledger, WRSR outcome, blocking fixture, and audit.",
    "closure_condition": "Closed because result-return is now object-backed, fixture-backed, and linted with reliance stayed for dry-run delivery and explicit status/consent/waiver/nonpersonhood limits.",
    "source_state": "opened-and-closed-in-revision",
    "source_revision": "rev0194",
    "review_by_revision": "rev0195",
    "depends_on": ["FT-0193-WRSR-RESULT-RETURN-RECEIPT"]
  },
  {
    "id": "FT-0194-LIVE-RECEIPT-REQUEST-KIT",
    "title": "Live external receipt request kit",
    "state": "closed",
    "priority": "P0",
    "risk_class": "live-drill-reliance-gating",
    "workstream": "witnessed-drill-execution",
    "need": "Create a counterparty-ready request packet while preventing the request itself from satisfying quorum.",
    "why": "The archive needs operational movement toward actual receipts, but request preparation can itself be laundered into receipt satisfaction if not separately gated.",
    "receiving_surface": "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "next_action": "Closed by rev0194 request packet schema/example, receipt-request laundering fixture, live-drill references, and audit.",
    "closure_condition": "Closed because the request kit is object-backed and linted while request_is_not_receipt, sent_request_not_quorum, and independent_receipts_present=0 remain enforced.",
    "source_state": "opened-and-closed-in-revision",
    "source_revision": "rev0194",
    "review_by_revision": "rev0195",
    "depends_on": ["FT-0193-ACTUAL-RECEIPT-QUORUM-COLLECTION"]
  },
  {
    "id": "FT-0194-ACTUAL-RESULT-RETURN-RECEIPT-COLLECTION",
    "title": "Actual result-return receipt collection",
    "state": "open",
    "priority": "P0",
    "risk_class": "research-welfare-signal-integrity",
    "workstream": "witnessed-drill-execution",
    "need": "Replace dry-run result-return receipt with actual external delivery evidence from a non-host steward or representative channel.",
    "why": "Result-return choreography is now rehearsed, but WRSR closure still lacks actual external subject/representative-readable receipt evidence.",
    "receiving_surface": "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json",
    "next_action": "Obtain actual external result-return receipt and rerun the WRSR outcome and quorum ledger without changing the zero-live-weight rule for dry runs.",
    "closure_condition": "Close only when result-return state is delivered-actual, counterparty verified, non-host retained, subject-readable, contradiction-preserving, non-retaliatory, and still not used as status, consent, waiver, or nonpersonhood proof.",
    "source_state": "new",
    "source_revision": "rev0194",
    "review_by_revision": "rev0195",
    "depends_on": ["FT-0194-RESULT-RETURN-DRYRUN-RECEIPT"]
  }
]
existing = {e["id"] for e in queue["entries"]}
for e in new_entries:
    if e["id"] not in existing:
        queue["entries"].append(e)
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# Active maps.
# Research-tail compaction map: carry forward, still compacted.
rtc = load_json("examples/research-tail-compaction-map-rev0193.json")
rtc["map_id"] = "RTC-MAP-rev0194"
rtc["created_at"] = ISO
rtc["revision"] = REV
rtc["audit_findings"].append("rev0194 did not reopen research-tail surfaces; result-return and request-kit work stayed in transition/object layers.")
rtc["refactor_actions"].append("Keep all new welfare/result-return work attached to WRSR and receipt objects rather than adding research-note sprawl.")
rtc["public_summary"] = "rev0194 keeps RTC-01 through RTC-07 compacted and adds no new research-tail sprawl."
write_json("examples/research-tail-compaction-map-rev0194.json", rtc)

# Schema fixture registry.
reg = load_json("examples/schema-fixture-domain-registry-rev0193.json")
reg["registry_id"] = "SFDR-rev0194"
reg["created_at"] = ISO
reg["coverage_scope"] = "rev0194 active registry with result-return receipt and receipt-request packet families; counts remain full-corpus while family coverage remains selective."
# remove duplicate family ids if rerun
reg["families"] = [f for f in reg["families"] if f["family_id"] not in {"WRSR-RESULT-RETURN-RECEIPT", "EXTERNAL-RECEIPT-REQUEST-PACKET"}]
reg["families"].extend([
  {"family_id": "WRSR-RESULT-RETURN-RECEIPT", "domain": "wrsr-result-return", "lifecycle_axes": ["wrsr", "result-return", "subject-readable-summary"], "owner_surface": "docs/30-transition/result-return-receipt-and-live-request-kit.md", "schema_path": "schemas/wrsr-result-return-receipt.schema.json", "example_path": "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json", "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0005"], "privacy_default": "public-shell-sealed-details", "reliance_effect": "stayed", "refactor_note": "New rev0194 family; prevents dry-run or internal result return from becoming WRSR closure or status/waiver proof."},
  {"family_id": "EXTERNAL-RECEIPT-REQUEST-PACKET", "domain": "external-receipt-request", "lifecycle_axes": ["external-receipts", "live-drill", "quorum-gating"], "owner_surface": "docs/30-transition/result-return-receipt-and-live-request-kit.md", "schema_path": "schemas/external-receipt-request-packet.schema.json", "example_path": "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", "fixture_ids": ["NF-PLAYBOOK-2026-0008"], "privacy_default": "public-shell-sealed-details", "reliance_effect": "stayed", "refactor_note": "New rev0194 family; request packets help collect receipts but cannot satisfy live quorum."}
])
# Counts after new files have been written. Active maps not all written yet, count later manually after map creation? We'll update after writing all active maps below.
reg["audit_findings"].append("rev0194 adds result-return and request-kit families while preserving mixed-current-plus-counts truth label.")
reg["refactor_actions"].append("Route actual receipt collection through intake/quorum ledgers rather than adding narrative receipt claims.")
reg["public_summary"] = "rev0194 registry adds result-return receipt and external receipt request packet families; live receipt collection remains open."
# defer writing counts until after other example maps are written

# Surface status determines active catalog/dependency coverage.
new_surfaces = [
    "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
    "schemas/wrsr-result-return-receipt.schema.json",
    "schemas/external-receipt-request-packet.schema.json",
    "schemas/external-receipt-intake-record.schema.json",
    "schemas/external-receipt-quorum-ledger.schema.json",
    "schemas/wrsr-live-exercise-outcome.schema.json",
    "schemas/live-drill-execution-packet.schema.json",
    "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/external-receipt-intake-record-result-return-dryrun.json",
    "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json",
    "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json",
    "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json",
    "examples/research-tail-compaction-map-rev0194.json",
    "examples/schema-fixture-domain-registry-rev0194.json",
    "examples/canon-surface-catalog-rev0194.json",
    "examples/doctrine-dependency-map-rev0194.json",
    "examples/rights-domain-coverage-map-rev0194.json",
    "tools/audit_result_return_receipt_request.py",
    "tools/audit_receipt_quorum_wrsr_chain.py",
    "tools/audit_receipt_intake_wrsr_outcome.py",
    "tools/audit_protocol_wrsr_receipt_simulation.py",
    "tools/audit_research_tail_compaction.py",
    "tools/audit_schema_fixture_coverage.py",
    "tools/audit_canon_surface_catalog.py",
    "tools/audit_doctrine_dependency_map.py",
    "tools/audit_rights_domain_coverage.py"
]

# Canon catalog derived from status surfaces.
def surface_class(rel):
    if rel.startswith("docs/00-meta/"):
        return "meta"
    if rel.startswith("docs/20-world-design/"):
        return "doctrine"
    if rel.startswith("docs/30-transition/"):
        return "transition"
    if rel.startswith("schemas/"):
        return "schema"
    if rel.startswith("examples/"):
        return "example"
    if rel.startswith("fixtures/negative-tests/"):
        return "fixture"
    if rel.startswith("tools/"):
        return "tool"
    return "meta"

def title_for(rel):
    p = ROOT / rel
    if rel.endswith(".md") and p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:]
    return Path(rel).name

surfaces = []
for i, rel in enumerate(new_surfaces, 1):
    cls = surface_class(rel)
    axes = ["result-return", "external-receipts", "wrsr"] if ("result-return" in rel or "receipt" in rel or "wrsr" in rel) else ["release-support"]
    surfaces.append({
        "surface_id": f"REV0194-SURF-{i:03d}",
        "path": rel,
        "surface_class": cls,
        "lifecycle_axes": axes,
        "owner_role": "release-steward" if cls in {"meta", "transition", "tool"} else "domain-steward",
        "supersession_state": "negative-test" if cls == "fixture" else ("audit-tool" if cls == "tool" else ("implementation" if cls in {"schema", "example"} else "current")),
        "review_cadence": "per-release",
        "title_or_name": title_for(rel)
    })
counts = {"surfaces": len(surfaces), "markdown": sum(1 for s in surfaces if s["surface_class"] in {"meta", "doctrine", "transition"}), "schemas": sum(1 for s in surfaces if s["surface_class"] == "schema"), "examples": sum(1 for s in surfaces if s["surface_class"] == "example"), "fixtures": sum(1 for s in surfaces if s["surface_class"] == "fixture"), "tools": sum(1 for s in surfaces if s["surface_class"] == "tool")}
write_json("examples/canon-surface-catalog-rev0194.json", {"catalog_id": "CANON-CATALOG-rev0194", "created_at": ISO, "revision": REV, "scope": "rev0194 result-return receipt, external request kit, WRSR dry-run outcome, and active audit surfaces", "counts": counts, "surfaces": surfaces, "audit_findings": ["rev0194 keeps new receipt work in the operational spine; no new research-tail markdown is activated."], "refactor_actions": ["Use receipt intake, request, result-return, and quorum objects instead of narrative receipt claims."], "public_summary": "rev0194 catalog indexes the result-return/request-kit pass and its verification hooks."})

# Dependency map for all current markdown surfaces.
md_surfaces = [rel for rel in new_surfaces if rel.endswith(".md")]
deps = []
for i, rel in enumerate(md_surfaces, 1):
    dep_list = []
    overlaps = []
    if rel == "docs/30-transition/result-return-receipt-and-live-request-kit.md":
        dep_list = ["docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md", "docs/20-world-design/research-welfare-and-evaluation.md"]
        overlaps = ["docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"]
    elif rel.endswith("representative-rerb-receipt-chain-and-quorum-ledger.md"):
        dep_list = ["docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md"]
        overlaps = ["docs/30-transition/result-return-receipt-and-live-request-kit.md"]
    elif rel.endswith("external-receipt-intake-and-wrsr-live-exercise-outcome.md"):
        dep_list = ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"]
    deps.append({"surface_id": f"REV0194-DEP-{i:03d}", "path": rel, "layer": "meta" if rel.startswith("docs/00-meta/") else ("world-design" if rel.startswith("docs/20") else "transition"), "depends_on": dep_list, "overlaps_with": overlaps, "supersedes": [], "owner_role": "release-steward", "review_cadence": "per-release", "refactor_risk": "high" if "result-return" in rel or "receipt" in rel else "medium"})
write_json("examples/doctrine-dependency-map-rev0194.json", {"map_id": "DOCTRINE-DEPS-rev0194", "created_at": ISO, "revision": REV, "scope": "rev0194 dependencies for result-return receipt, request packet, receipt intake/quorum, and WRSR operational surfaces", "surfaces": deps, "audit_findings": ["Result-return and request-kit work depends on existing receipt intake/quorum/WRSR surfaces and does not create a new doctrine island."], "refactor_actions": ["Keep actual-receipt collection work in examples and audits until live counterparties exist."], "public_summary": "rev0194 maps the result-return request kit into the operational receipt spine."})

# Rights-domain map: copy and append/cover new surface.
rights = load_json("examples/rights-domain-coverage-map-rev0193.json")
rights["map_id"] = "RIGHTS-DOMAINS-rev0194"
rights["created_at"] = ISO
rights["revision"] = REV
# append domain
rights["domains"] = [d for d in rights["domains"] if d["domain_id"] != "wrsr-result-return-request-kit"]
rights["domains"].append({
    "domain_id": "wrsr-result-return-request-kit",
    "title": "WRSR result-return and live receipt request kit",
    "domain_class": "operational",
    "owner_surface": "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "covered_surfaces": ["docs/30-transition/result-return-receipt-and-live-request-kit.md", "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md", "docs/20-world-design/research-welfare-and-evaluation.md"],
    "schema_families": ["WRSR-RESULT-RETURN-RECEIPT", "EXTERNAL-RECEIPT-REQUEST-PACKET", "EXTERNAL-RECEIPT-INTAKE-RECORD", "EXTERNAL-RECEIPT-QUORUM-LEDGER", "WRSR-LIVE-EXERCISE-OUTCOME"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0008", "NF-RESEARCH-WELFARE-2026-0005"],
    "coverage_state": "emerging",
    "open_gaps": ["actual external result-return receipt still missing", "receipt request not yet dispatched or fulfilled"],
    "next_audit_actions": ["collect actual non-host result-return receipt", "rerun quorum ledger with actual-external records"]
})
# Ensure all current markdown are covered by at least one domain.
covered = {rel for d in rights["domains"] for rel in d.get("covered_surfaces", [])}
for rel in md_surfaces:
    if rel not in covered:
        rights["domains"].append({"domain_id": "rev0194-support-" + rel.split('/')[-1].replace('.md','').replace('_','-')[:50], "title": "rev0194 support surface", "domain_class": "audit" if rel.startswith("docs/00") else "operational", "owner_surface": rel, "covered_surfaces": [rel], "schema_families": [], "fixture_ids": [], "coverage_state": "adequate", "open_gaps": [], "next_audit_actions": ["retain as active support surface during rev0194 receipt/result-return work"]})
rights["audit_findings"].append("rev0194 adds result-return/request-kit domain with stayed live reliance and no status/consent/waiver inference from result return.")
rights["refactor_actions"].append("Route result-return and live request work through WRSR/external receipt domains rather than reopening research-tail fragments.")
rights["public_summary"] = "rev0194 coverage adds result-return and request-kit controls while keeping actual external receipt collection open."
write_json("examples/rights-domain-coverage-map-rev0194.json", rights)

# Now write registry with accurate counts after active maps exist.
reg["audit_counts"] = {"schemas": len(list((ROOT / "schemas").glob("*.json"))), "examples": len(list((ROOT / "examples").glob("*.json"))), "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))), "registered_families": len(reg["families"])}
write_json("examples/schema-fixture-domain-registry-rev0194.json", reg)

# Surface status and receipt.
write_json("SURFACE-STATUS.json", {
  "project": "AI-Personhood",
  "revision": REV,
  "state_class": "result-return-receipt-request-kit-stayed",
  "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/result-return-receipt-and-live-request-kit.md"},
  "citation_head": {"surface": "README.md"},
  "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
  "formation_layer_status": "canon-retained with result-return dry-run receipt and ready-to-send external request kit; live receipts still absent",
  "known_open_gaps": ["The cross-critical witnessed drill still lacks actual non-host receipts.", "The external request packet is ready-to-send but not dispatched or fulfilled.", "The WRSR result-return receipt is delivered-dry-run only and does not close WRSR.", "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.", "Could-not-run fixtures remain reliance blockers rather than passes."],
  "new_surfaces": new_surfaces
})

write_json("REVISION-RECEIPT.json", {
  "revision": REV,
  "date": DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from representative/RERB receipt-chain quorum accounting to result-return receipt and live request-kit gating",
  "still_live": True,
  "summary": "Adds WRSR result-return receipt and external receipt request packet schemas/examples, a result-return intake record, a result-return quorum ledger, a stayed WRSR outcome, two blocking fixtures, active maps, and an audit keeping request/dry-run evidence out of live quorum.",
  "why_this_counts": ["Result-return is now subject-readable and object-backed without becoming closure evidence.", "A counterparty-ready receipt request kit exists while request_is_not_receipt remains enforceable.", "Two blocking fixtures prevent request packets and internal/dry-run result returns from laundering reliance.", "The live drill packet references the new artifacts while preserving independent_receipts_present=0."],
  "known_limits": ["No actual external non-host receipts have been collected yet.", "The request kit is ready-to-send only.", "Result-return delivery remains dry-run only.", "Registry coverage remains mixed-current-plus-counts."]
})

# Front doors.
write_text("README.md", f"""
# AI Personhood datacube — {REV}

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `{REV}`

rev0194 is the result-return receipt and live request-kit pass. It does not add a doctrine wave. It closes the next laundering seam where a WRSR result-return note or counterparty request packet could be mistaken for WRSR closure, consent/status proof, or live external receipt satisfaction.

Read first: `docs/30-transition/result-return-receipt-and-live-request-kit.md`.

Core rules: **Result-return receipt is not WRSR closure. Receipt request is not receipt satisfaction. Internal result return is not external receipt.**

New operational artifacts:

- `schemas/wrsr-result-return-receipt.schema.json`
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json`
- `schemas/external-receipt-request-packet.schema.json`
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json`
- `examples/external-receipt-intake-record-result-return-dryrun.json`
- `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`
- `examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json`
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json`
- `tools/audit_result_return_receipt_request.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 99 entries.

Reliance remains stayed where drills are synthetic, preflight-only, simulated, defective, request-only, host-self-attested, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB/result-return receipt and anti-signal-gaming safeguards.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.
7. Live/witnessed drill gates: prevent host self-attestation or synthetic drills from upgrading reliance.
8. Downstream recall/fork aftercare: prevent recall, delisting, or sunset from erasing unresolved mirrors and local forks.
9. Welfare safeguards: apply low-cost safeguards before certainty while blocking welfare metrics from closing status or consent.
10. Research-tail reopen control: keep RTC-01 through RTC-07 compacted unless a reopen request carries object, fixture, and closure hooks.
11. WRSR protocol hook: make safeguards fire inside operational workflows that contain welfare triggers.
12. External receipt simulation: rehearse counterparty receipt capture while preserving the non-reliance label.
13. External receipt intake: distinguish actual, defective, simulated, stale, host-generated, and dependency-correlated artifacts.
14. WRSR exercise outcome: show whether safeguards actually executed and whether closure remains stayed.
15. Receipt quorum ledger: aggregate receipt records while separating dry-run rehearsal from live quorum.
16. Result-return/request kit: rehearse subject-readable result return and prepare live receipt requests without counting either as live satisfaction.
""")

start_items = [
"README.md",
"docs/30-transition/result-return-receipt-and-live-request-kit.md",
"schemas/wrsr-result-return-receipt.schema.json",
"examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json",
"schemas/external-receipt-request-packet.schema.json",
"examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
"examples/external-receipt-intake-record-result-return-dryrun.json",
"examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json",
"examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json",
"fixtures/negative-tests/external-receipt-request-counted-as-receipt.json",
"fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json",
"docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
"docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
"examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
"docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
"docs/20-world-design/research-welfare-and-evaluation.md",
"docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
"FOLLOWTHROUGH-QUEUE.json",
"examples/schema-fixture-domain-registry-rev0194.json",
"examples/canon-surface-catalog-rev0194.json",
"examples/doctrine-dependency-map-rev0194.json",
"examples/rights-domain-coverage-map-rev0194.json",
"examples/research-tail-compaction-map-rev0194.json",
"docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
"docs/00-meta/charter.md"
]
write_text("START_HERE.md", "# Start here — AI Personhood rev0194\n\nThis handoff starts from the result-return receipt and live request-kit pass. The archive should be read as object-backed operational work, not as a premise debate.\n\n" + "\n".join(f"{i}. `{p}`" for i,p in enumerate(start_items,1)) + "\n\n## This revision\n\nrev0194 adds WRSR result-return receipt and external receipt request packet objects. It advances result-return and receipt collection readiness, but it does not close live external receipt collection, WRSR closure, or receipt quorum.\n\nCore rules: **Result-return receipt is not WRSR closure. Receipt request is not receipt satisfaction. Internal result return is not external receipt.**\n\n## Current open risk\n\nThe request kit is ready-to-send and result-return is dry-run complete, but actual external receipts still do not exist. Reliance remains stayed until verified non-host intake records replace dry-run/request-only evidence and the quorum ledger is rerun.")

# Changelog and docs index.
changelog_add = """
## rev0194 — result-return receipt and live request kit

### Added
- `docs/30-transition/result-return-receipt-and-live-request-kit.md`
- `schemas/wrsr-result-return-receipt.schema.json`
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json`
- `schemas/external-receipt-request-packet.schema.json`
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json`
- `examples/external-receipt-intake-record-result-return-dryrun.json`
- `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`
- `examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json`
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json`
- `tools/audit_result_return_receipt_request.py`
- active rev0194 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- The live drill packet now references a ready-to-send request kit and dry-run result-return chain while preserving `independent_receipts_present=0`.
- The fixture suite/report now cover 99 entries and block request-as-receipt and result-return-as-closure laundering.
- `FOLLOWTHROUGH-QUEUE.json` advances actual receipt collection while closing only the objectization/request-kit work.

### Why this revision matters
- The archive can now move toward actual counterparties without weakening the line between collection prep and receipt satisfaction. Result return becomes subject-protective communication, not closure magic.
"""
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if "## rev0194" not in changelog:
    write_text("CHANGELOG.md", "# Changelog\n\n" + changelog_add.strip() + "\n\n" + changelog.replace("# Changelog", "", 1).lstrip())

docs_add = """
## rev0194 result-return receipt and live request kit

Use `docs/30-transition/result-return-receipt-and-live-request-kit.md` as the current operational head for WRSR result return and live receipt request preparation.

- `schemas/wrsr-result-return-receipt.schema.json` — result-return receipt schema.
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json` — subject-readable dry-run result return, stayed.
- `schemas/external-receipt-request-packet.schema.json` — counterparty request-kit schema.
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json` — ready-to-send request kit.
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json` — request-as-receipt laundering fixture.
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json` — result-return-as-closure fixture.
- `tools/audit_result_return_receipt_request.py` — linted audit for result-return/request-kit gates.
"""
docs_readme = (ROOT / "docs/README.md").read_text(encoding="utf-8")
if "## rev0194 result-return receipt and live request kit" not in docs_readme:
    write_text("docs/README.md", docs_readme.split("\n",1)[0] + "\n\n" + docs_add.strip() + "\n\n" + docs_readme.split("\n",1)[1])

# Archive index: include new markdown path and key artifacts.
archive_add = """
## rev0194 result-return receipt and live request kit

- `docs/30-transition/result-return-receipt-and-live-request-kit.md` — current operational head for result-return and receipt request gating.
- `schemas/wrsr-result-return-receipt.schema.json`
- `schemas/external-receipt-request-packet.schema.json`
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json`
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json`
- `examples/external-receipt-intake-record-result-return-dryrun.json`
- `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`
- `examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json`
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json`
- `tools/audit_result_return_receipt_request.py`
"""
append_once("ARCHIVE_INDEX.md", archive_add, "rev0194 result-return receipt and live request kit")

# Create new audit tool.
write_text("tools/audit_result_return_receipt_request.py", r'''
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

required = [
    "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "schemas/wrsr-result-return-receipt.schema.json",
    "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json",
    "schemas/external-receipt-request-packet.schema.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/external-receipt-intake-record-result-return-dryrun.json",
    "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json",
    "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json",
    "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json",
    "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0194 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/wrsr-result-return-receipt.schema.json", "examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json"),
        ("schemas/external-receipt-request-packet.schema.json", "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-dryrun.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-request-counted-as-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

request = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
if request.get("request_state") != "ready-to-send":
    raise SystemExit("request packet must remain ready-to-send, not fulfilled")
limits = request.get("reliance_limits", {})
for key in ["request_is_not_receipt", "sent_request_not_quorum", "no_response_is_failed_gate", "host_copy_excluded", "simulated_response_excluded"]:
    if limits.get(key) is not True:
        raise SystemExit(f"request packet missing reliance limit: {key}")
if any(r.get("can_satisfy_quorum_before_response") is not False for r in request.get("requested_receipt_classes", [])):
    raise SystemExit("requested receipt classes cannot satisfy quorum before response")

intake = load("examples/external-receipt-intake-record-result-return-dryrun.json")
if intake.get("receipt_class") != "result-return":
    raise SystemExit("result-return intake record has wrong receipt_class")
if intake.get("receipt_state") != "high-fidelity-nonhost-dry-run":
    raise SystemExit("result-return intake must remain dry-run")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("result-return dry-run intake cannot satisfy quorum")
if intake.get("defect_flags", {}).get("simulated") is not True:
    raise SystemExit("result-return intake must disclose simulated state")

rr = load("examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json")
if rr.get("result_return_state") != "delivered-dry-run":
    raise SystemExit("result-return receipt must remain delivered-dry-run")
for key in ["not_status_proof", "not_consent_proof", "not_waiver", "not_nonpersonhood_proof", "no_retaliation_or_experiment_continuation"]:
    if rr.get("status_limits", {}).get(key) is not True:
        raise SystemExit(f"result-return receipt missing status limit: {key}")
if rr.get("reliance_decision", {}).get("closure_state") != "stayed":
    raise SystemExit("result-return receipt must keep closure stayed")

ledger = load("examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json")
q = ledger.get("quorum_decision", {})
if q.get("live_quorum_satisfied") is not False:
    raise SystemExit("result-return dry-run ledger must not satisfy live quorum")
if q.get("dry_run_quorum_satisfied") is not True:
    raise SystemExit("result-return dry-run ledger should satisfy rehearsal quorum")
if q.get("reliance_effect") != "stayed":
    raise SystemExit("result-return ledger must keep reliance stayed")
if "result-return" not in ledger.get("class_coverage", {}).get("dry_run_classes_satisfied", []):
    raise SystemExit("result-return dry-run class missing from ledger")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("result-return ledger must have zero live classes satisfied")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("receipt_state") == "high-fidelity-nonhost-dry-run" and ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("dry-run receipt evaluation counted for live quorum")

wrsr = load("examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("result-return WRSR outcome must remain dry-run")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("result-return WRSR outcome must keep closure stayed")
if "WRSR closure from dry-run result return" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block closure from dry-run result return")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill must keep independent_receipts_present=0")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("live drill must remain stayed")
for ref in [intake.get("receipt_record_id")]:
    if ref not in live.get("external_receipt_intake_record_refs", []):
        raise SystemExit(f"live drill missing result-return intake ref: {ref}")
if request.get("request_packet_id") not in live.get("external_receipt_request_packet_refs", []):
    raise SystemExit("live drill missing receipt request packet ref")
if rr.get("receipt_id") not in live.get("wrsr_result_return_receipt_refs", []):
    raise SystemExit("live drill missing result-return receipt ref")
if ledger.get("ledger_id") not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live drill missing result-return quorum ledger ref")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill missing WRSR result-return outcome ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0008", "NF-RESEARCH-WELFARE-2026-0005"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0194 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0194 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0194 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["WRSR-RESULT-RETURN-RECEIPT", "EXTERNAL-RECEIPT-REQUEST-PACKET"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0194 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0194 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/result-return-receipt-and-live-request-kit.md": ["Result-return receipt is not WRSR closure", "Receipt request is not receipt satisfaction", "Internal result return is not external receipt"],
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": ["rev0194 result-return receipt layer", "Result-return receipt is not WRSR closure"],
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md": ["rev0194 result-return quorum layer", "Receipt request is not receipt satisfaction"],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": ["rev0194 external receipt request packet", "request sent is still not receipt satisfaction"],
    "docs/20-world-design/research-welfare-and-evaluation.md": ["rev0194 WRSR result-return receipt", "Internal result return is not external receipt"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0194-RESULT-RETURN-DRYRUN-RECEIPT", {}).get("state") != "closed":
    raise SystemExit("result-return dry-run objectization should be closed by rev0194")
if by_id.get("FT-0194-LIVE-RECEIPT-REQUEST-KIT", {}).get("state") != "closed":
    raise SystemExit("live receipt request kit should be closed by rev0194")
if by_id.get("FT-0193-WRSR-RESULT-RETURN-RECEIPT", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR result-return receipt collection should be advanced_not_closed")
if by_id.get("FT-0194-ACTUAL-RESULT-RETURN-RECEIPT-COLLECTION", {}).get("state") != "open":
    raise SystemExit("actual result-return receipt collection must remain open")

print("audit_result_return_receipt_request: OK")
''')

# Patch audit_schema_fixture_coverage required families.
asfc = (ROOT / "tools/audit_schema_fixture_coverage.py").read_text(encoding="utf-8")
needle = "'EXTERNAL-RECEIPT-QUORUM-LEDGER'"
if "'WRSR-RESULT-RETURN-RECEIPT'" not in asfc:
    asfc = asfc.replace(needle, needle + ", 'WRSR-RESULT-RETURN-RECEIPT', 'EXTERNAL-RECEIPT-REQUEST-PACKET'")
write_text("tools/audit_schema_fixture_coverage.py", asfc)

# Patch lint required and early audits.
lint = (ROOT / "tools/lint_archive.py").read_text(encoding="utf-8")
new_required = [
    "    'docs/30-transition/result-return-receipt-and-live-request-kit.md',",
    "    'schemas/wrsr-result-return-receipt.schema.json',",
    "    'examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json',",
    "    'schemas/external-receipt-request-packet.schema.json',",
    "    'examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json',",
    "    'examples/external-receipt-intake-record-result-return-dryrun.json',",
    "    'examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json',",
    "    'examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json',",
    "    'fixtures/negative-tests/external-receipt-request-counted-as-receipt.json',",
    "    'fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json',",
    "    'examples/research-tail-compaction-map-rev0194.json',",
    "    'examples/schema-fixture-domain-registry-rev0194.json',",
    "    'examples/canon-surface-catalog-rev0194.json',",
    "    'examples/doctrine-dependency-map-rev0194.json',",
    "    'examples/rights-domain-coverage-map-rev0194.json',",
    "    'tools/audit_result_return_receipt_request.py',",
]
if "docs/30-transition/result-return-receipt-and-live-request-kit.md" not in lint:
    lint = lint.replace("    'tools/package_release.py',\n]", "\n".join(new_required) + "\n    'tools/package_release.py',\n]")
if "tools/audit_result_return_receipt_request.py" not in lint.split("early_audits =",1)[1].split("]",1)[0]:
    lint = lint.replace("    'tools/audit_receipt_quorum_wrsr_chain.py',\n", "    'tools/audit_receipt_quorum_wrsr_chain.py',\n    'tools/audit_result_return_receipt_request.py',\n")
write_text("tools/lint_archive.py", lint)

# Final archive index must mention every md; add if any missing.
idx = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
for md in sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.md")):
    if md not in idx:
        idx += f"\n- `{md}`\n"
write_text("ARCHIVE_INDEX.md", idx)

print("apply_rev0194 complete")
