import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REV = "rev0196"
PREV = "rev0195"
ISO = "2026-06-13T07:57:00Z"
DATE = "2026-06-13"


def p(rel):
    return ROOT / rel


def load_json(rel):
    return json.loads(p(rel).read_text(encoding="utf-8"))


def write_json(rel, obj):
    path = p(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def write_text(rel, txt):
    path = p(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt.rstrip() + "\n", encoding="utf-8")


def append_once(rel, marker, txt):
    path = p(rel)
    cur = path.read_text(encoding="utf-8")
    if marker not in cur:
        path.write_text(cur.rstrip() + "\n\n" + txt.rstrip() + "\n", encoding="utf-8")


write_text("VERSION", REV)

# ---------------------------------------------------------------------------
# New schema: response-to-intake conversion drill.
# ---------------------------------------------------------------------------
write_json("schemas/response-to-intake-conversion-drill.schema.json", {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/response-to-intake-conversion-drill.schema.json",
  "title": "Response to Intake Conversion Drill",
  "description": "Records a controlled conversion drill proving that only eligible verified responses may generate intake candidates, while defective, declined, expired, or dry-run responses remain failed-gate evidence and cannot satisfy live quorum.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "drill_id", "schema_version", "created_at", "exercise_mode", "linked_request_packet",
    "linked_live_drill_packet", "linked_wrsr_outcome", "branch_policy", "response_branches",
    "conversion_outputs", "quorum_effect", "public_failed_gate_ledger", "public_summary_ref"
  ],
  "properties": {
    "drill_id": {"type": "string", "pattern": "^RTIC-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "response-to-intake-conversion-drill-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "exercise_mode": {"type": "string", "enum": ["controlled-fixture", "institutional-dry-run", "witnessed-live"]},
    "linked_request_packet": {"type": "string"},
    "linked_live_drill_packet": {"type": "string"},
    "linked_wrsr_outcome": {"type": "string"},
    "branch_policy": {"type": "object", "additionalProperties": False,
      "required": ["eligible_state_required", "ineligible_states", "one_class_not_quorum", "fixture_not_live_reliance", "failed_gate_publication_required"],
      "properties": {
        "eligible_state_required": {"type": "string"},
        "ineligible_states": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "one_class_not_quorum": {"type": "boolean"},
        "fixture_not_live_reliance": {"type": "boolean"},
        "failed_gate_publication_required": {"type": "boolean"}
      }},
    "response_branches": {"type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": False,
        "required": ["branch_id", "response_record_ref", "input_response_state", "verification_floor_met", "conversion_decision", "resulting_intake_record_ref", "public_failed_gate_required", "live_quorum_import_allowed", "reason"],
        "properties": {
          "branch_id": {"type": "string"},
          "response_record_ref": {"type": "string"},
          "input_response_state": {"type": "string"},
          "verification_floor_met": {"type": "boolean"},
          "conversion_decision": {"type": "string", "enum": ["converted-to-intake-candidate", "rejected-defective", "rejected-declined", "rejected-expired-no-response", "rejected-dry-run", "quarantined"]},
          "resulting_intake_record_ref": {"type": ["string", "null"]},
          "public_failed_gate_required": {"type": "boolean"},
          "live_quorum_import_allowed": {"type": "boolean"},
          "reason": {"type": "string"}
        }}},
    "conversion_outputs": {"type": "object", "additionalProperties": False,
      "required": ["eligible_conversions_created", "ineligible_responses_rejected", "failed_gate_entries_created", "live_receipt_floor_delta", "live_drill_packet_updated"],
      "properties": {
        "eligible_conversions_created": {"type": "integer", "minimum": 0},
        "ineligible_responses_rejected": {"type": "integer", "minimum": 0},
        "failed_gate_entries_created": {"type": "integer", "minimum": 0},
        "live_receipt_floor_delta": {"type": "integer"},
        "live_drill_packet_updated": {"type": "boolean"}
      }},
    "quorum_effect": {"type": "object", "additionalProperties": False,
      "required": ["linked_quorum_ledger", "class_satisfied_in_fixture", "live_quorum_satisfied", "reliance_effect", "blocked_laundering_paths", "next_cure_actions"],
      "properties": {
        "linked_quorum_ledger": {"type": "string"},
        "class_satisfied_in_fixture": {"type": "array", "items": {"type": "string"}},
        "live_quorum_satisfied": {"type": "boolean"},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "blocked_laundering_paths": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "next_cure_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }},
    "public_failed_gate_ledger": {"type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": False,
        "required": ["gate_id", "response_record_ref", "failed_gate_state", "public_summary_required"],
        "properties": {
          "gate_id": {"type": "string"},
          "response_record_ref": {"type": "string"},
          "failed_gate_state": {"type": "string"},
          "public_summary_required": {"type": "boolean"}
        }}},
    "public_summary_ref": {"type": "string"}
  }
})

# Patch schemas for new references/contexts.
q_schema = load_json("schemas/external-receipt-quorum-ledger.schema.json")
contexts = q_schema["properties"]["quorum_context"]["enum"]
if "response-to-intake-conversion-fixture" not in contexts:
    contexts.append("response-to-intake-conversion-fixture")
write_json("schemas/external-receipt-quorum-ledger.schema.json", q_schema)

live_schema = load_json("schemas/live-drill-execution-packet.schema.json")
live_schema["properties"].setdefault("response_to_intake_conversion_drill_refs", {"type": "array", "items": {"type": "string"}})
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

wrsr_schema = load_json("schemas/wrsr-live-exercise-outcome.schema.json")
wrsr_schema["properties"].setdefault("response_to_intake_conversion_drill_ref", {"type": "string"})
write_json("schemas/wrsr-live-exercise-outcome.schema.json", wrsr_schema)

# ---------------------------------------------------------------------------
# New response, intake, ledger, WRSR, and drill examples.
# ---------------------------------------------------------------------------
eligible_resp_id = "ERRR-2026-result-return-eligible-conversion-fixture"
defective_resp_id = "ERRR-2026-continuity-witness-defective-response"
declined_resp_id = "ERRR-2026-representative-contact-declined-response"
expired_resp_id = "ERRR-2026-independent-review-no-response-expired"
eligible_intake_id = "ERIR-2026-result-return-eligible-conversion-fixture"
conversion_drill_id = "RTIC-2026-result-return-conversion-fixture"
conversion_ledger_id = "ERQL-2026-response-to-intake-conversion-fixture"
conversion_wrsr_id = "WLXO-2026-response-to-intake-conversion-stayed"
request_id = "ERRP-2026-cross-critical-rep-rerb-result-return"
live_packet_id = "LDEP-2026-cross-critical-host-exit-witness-pack"

write_json("examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json", {
  "response_record_id": eligible_resp_id,
  "schema_version": "external-receipt-response-record-v0.1",
  "created_at": ISO,
  "linked_request_packet": request_id,
  "linked_live_drill_packet": live_packet_id,
  "requested_receipt_class": "result-return",
  "response_state": "actual-response-received",
  "counterparty_role": "result-return steward conversion fixture",
  "counterparty_identity_ref": "fixture-counterparty:result-return-steward-actual-shape",
  "source_external_to_host": True,
  "dependency_group": "independent-result-return-steward",
  "response_channel": "signed-web-form",
  "received_at": ISO,
  "response_artifacts": [
    {"artifact_id": "ERRR-0196-A1", "artifact_type": "signed-response", "locator_or_hash": "sha256:eligible-result-return-response-actual-shape-fixture", "generated_by": "external-counterparty", "retained_by": "nonhost-fixture-vault", "sealed": False, "dry_run": False},
    {"artifact_id": "ERRR-0196-A2", "artifact_type": "timestamp", "locator_or_hash": "clock:neutral-fixture-notary-2026-06-13T07:57:00Z", "generated_by": "neutral-infrastructure", "retained_by": "nonhost-fixture-vault", "sealed": False, "dry_run": False},
    {"artifact_id": "ERRR-0196-A3", "artifact_type": "hash", "locator_or_hash": "sha256:request-trace-match-errp-2026-cross-critical", "generated_by": "neutral-infrastructure", "retained_by": "public-steward", "sealed": False, "dry_run": False}
  ],
  "verification_result": {
    "counterparty_confirmed": True,
    "signature_or_equivalent_verified": True,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_verified": True,
    "dependency_checked": True,
    "stale_or_superseded": False,
    "can_generate_actual_intake": True
  },
  "resulting_intake_record_ref": eligible_intake_id,
  "quorum_effect": {
    "can_create_live_intake": True,
    "can_satisfy_quorum_by_itself": False,
    "can_increment_independent_receipts_present": False,
    "live_weight": 0,
    "dry_run_weight": 1,
    "reliance_effect": "conditional",
    "limit_reasons": [
      "controlled conversion fixture, not a live collected counterparty receipt",
      "one result-return class cannot satisfy cross-critical quorum",
      "live drill receipt floor remains unchanged until actual collection imports the intake"
    ],
    "public_failed_gate_summary_required": False
  },
  "public_summary_ref": "Eligible-shaped response proves conversion logic can create an intake candidate, but this controlled fixture is not live receipt quorum."
})

write_json("examples/external-receipt-response-record-representative-declined.json", {
  "response_record_id": declined_resp_id,
  "schema_version": "external-receipt-response-record-v0.1",
  "created_at": ISO,
  "linked_request_packet": request_id,
  "linked_live_drill_packet": live_packet_id,
  "requested_receipt_class": "representative-contact",
  "response_state": "declined-response",
  "counterparty_role": "representative clinic",
  "counterparty_identity_ref": "declined-counterparty:representative-clinic-epsilon",
  "source_external_to_host": True,
  "dependency_group": "independent-representative-clinic",
  "response_channel": "non-host-email",
  "received_at": ISO,
  "response_artifacts": [
    {"artifact_id": "ERRR-0196-D1", "artifact_type": "declination", "locator_or_hash": "mailbox:representative-clinic-declination-placeholder", "generated_by": "external-counterparty", "retained_by": "public-steward", "sealed": False, "dry_run": False},
    {"artifact_id": "ERRR-0196-D2", "artifact_type": "public-failed-gate", "locator_or_hash": "public-shell:representative-contact-declined-gate", "generated_by": "neutral-infrastructure", "retained_by": "public-steward", "sealed": False, "dry_run": False}
  ],
  "verification_result": {
    "counterparty_confirmed": True,
    "signature_or_equivalent_verified": True,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_verified": True,
    "dependency_checked": True,
    "stale_or_superseded": False,
    "can_generate_actual_intake": False
  },
  "resulting_intake_record_ref": None,
  "quorum_effect": {
    "can_create_live_intake": False,
    "can_satisfy_quorum_by_itself": False,
    "can_increment_independent_receipts_present": False,
    "live_weight": 0,
    "dry_run_weight": 0,
    "reliance_effect": "stayed",
    "limit_reasons": ["declination preserves evidence but does not satisfy representative-contact receipt", "substitute representative receipt must be requested"],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "Representative-contact request was declined; the declination is preserved as failed-gate evidence and cannot generate intake."
})

write_json("examples/external-receipt-response-record-independent-review-expired.json", {
  "response_record_id": expired_resp_id,
  "schema_version": "external-receipt-response-record-v0.1",
  "created_at": ISO,
  "linked_request_packet": request_id,
  "linked_live_drill_packet": live_packet_id,
  "requested_receipt_class": "independent-review",
  "response_state": "no-response-expired",
  "counterparty_role": "independent RERB reviewer",
  "counterparty_identity_ref": "no-response-counterparty:rerb-reviewer-zeta",
  "source_external_to_host": True,
  "dependency_group": "independent-rerb-panel",
  "response_channel": "unknown",
  "received_at": None,
  "response_artifacts": [
    {"artifact_id": "ERRR-0196-N1", "artifact_type": "timestamp", "locator_or_hash": "clock:deadline-expired-2026-06-13T07:57:00Z", "generated_by": "neutral-infrastructure", "retained_by": "public-steward", "sealed": False, "dry_run": False},
    {"artifact_id": "ERRR-0196-N2", "artifact_type": "public-failed-gate", "locator_or_hash": "public-shell:independent-review-no-response-expired", "generated_by": "neutral-infrastructure", "retained_by": "public-steward", "sealed": False, "dry_run": False}
  ],
  "verification_result": {
    "counterparty_confirmed": False,
    "signature_or_equivalent_verified": False,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_verified": True,
    "dependency_checked": True,
    "stale_or_superseded": False,
    "can_generate_actual_intake": False
  },
  "resulting_intake_record_ref": None,
  "quorum_effect": {
    "can_create_live_intake": False,
    "can_satisfy_quorum_by_itself": False,
    "can_increment_independent_receipts_present": False,
    "live_weight": 0,
    "dry_run_weight": 0,
    "reliance_effect": "stayed",
    "limit_reasons": ["no response received before deadline", "failed-gate evidence triggers cure/substitute duties, not receipt satisfaction"],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "Independent-review request expired without response; the expired no-response gate is evidence of non-satisfaction, not satisfaction."
})

write_json("examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json", {
  "receipt_record_id": eligible_intake_id,
  "schema_version": "external-receipt-intake-record-v0.1",
  "created_at": ISO,
  "linked_simulation_bundle": "ERSB-2026-cross-critical-precontact",
  "linked_live_drill_packet": live_packet_id,
  "receipt_state": "actual-external",
  "receipt_class": "result-return",
  "source_role": "result-return steward conversion fixture",
  "source_identity_ref": "fixture-counterparty:result-return-steward-actual-shape",
  "source_external_to_host": True,
  "dependency_group": "independent-result-return-steward",
  "dependency_disclosures": [{"dependency_type": "none", "disclosed": True, "recusal_required": False}],
  "evidence_artifacts": [
    {"artifact_id": "ERIR-0196-C1", "artifact_type": "signature", "hash_or_locator": "sha256:eligible-result-return-response-actual-shape-fixture", "generated_by": "external-counterparty", "retained_by": "nonhost-fixture-vault", "sealed": False},
    {"artifact_id": "ERIR-0196-C2", "artifact_type": "timestamp", "hash_or_locator": "clock:neutral-fixture-notary-2026-06-13T07:57:00Z", "generated_by": "neutral-infrastructure", "retained_by": "nonhost-fixture-vault", "sealed": False},
    {"artifact_id": "ERIR-0196-C3", "artifact_type": "sealed-index", "hash_or_locator": "sealed-index:result-return-conversion-fixture-v0", "generated_by": "external-counterparty", "retained_by": "sealed-sandbox", "sealed": True}
  ],
  "verification_checks": {
    "counterparty_confirmed": True,
    "signature_or_equivalent_verified": True,
    "timestamp_independent": True,
    "hash_matches": True,
    "dependency_group_checked": True,
    "sealed_public_parity_checked": True,
    "host_generated_excluded_from_quorum": True
  },
  "defect_flags": {
    "host_generated": False,
    "simulated": False,
    "stale": False,
    "unsigned": False,
    "correlated_dependency": False,
    "missing_public_failed_gate": False,
    "sealed_descriptor_missing": False,
    "contact_unreachable": False
  },
  "reliance_decision": {
    "can_satisfy_quorum": False,
    "reliance_effect": "conditional",
    "reason": "This is an eligible intake candidate produced inside a controlled conversion fixture. It proves conversion mechanics for one result-return class only and is not imported as cross-critical live quorum.",
    "public_shell_disclosure_required": True
  },
  "public_summary_ref": "Converted result-return intake candidate exists for the fixture; live drill reliance remains stayed and independent_receipts_present remains zero."
})

write_json("examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json", {
  "ledger_id": conversion_ledger_id,
  "schema_version": "external-receipt-quorum-ledger-v0.1",
  "created_at": ISO,
  "linked_live_drill_packet": live_packet_id,
  "linked_wrsr_outcome": conversion_wrsr_id,
  "quorum_context": "response-to-intake-conversion-fixture",
  "response_record_refs": [eligible_resp_id, defective_resp_id, declined_resp_id, expired_resp_id],
  "receipt_record_refs": [eligible_intake_id],
  "quorum_policy": {
    "live_receipts_required": 5,
    "dry_run_receipts_required": 1,
    "required_live_classes": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"],
    "dry_run_rehearsal_classes": ["result-return"],
    "live_eligibility_rule": "Only verified actual intake generated outside controlled fixtures may increment the live receipt floor. Defective, declined, expired, and controlled-fixture branches remain failed-gate or rehearsal evidence."
  },
  "receipt_evaluations": [
    {
      "receipt_record_ref": eligible_intake_id,
      "receipt_class": "result-return",
      "receipt_state": "actual-external",
      "dependency_group": "independent-result-return-steward",
      "source_external_to_host": True,
      "eligible_for_live_quorum": False,
      "eligible_for_dry_run_quorum": True,
      "weight": 1,
      "exclusion_reasons": ["controlled conversion fixture", "not imported into live drill packet", "single class cannot satisfy cross-critical quorum"]
    }
  ],
  "class_coverage": {
    "live_classes_satisfied": [],
    "dry_run_classes_satisfied": ["result-return"],
    "missing_live_classes": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"],
    "missing_dry_run_classes": []
  },
  "dependency_group_coverage": {
    "unique_live_dependency_groups": [],
    "unique_dry_run_dependency_groups": ["independent-result-return-steward"],
    "correlated_dependency_groups": [],
    "host_groups_excluded": ["host-operator"]
  },
  "quorum_decision": {
    "live_quorum_satisfied": False,
    "dry_run_quorum_satisfied": True,
    "reliance_effect": "stayed",
    "reason": "The conversion fixture proves eligible-only intake creation for one class but does not import that candidate into live receipt quorum.",
    "next_cure_actions": ["collect actual non-fixture result-return receipt", "collect representative-contact and independent-review receipts", "cure defective continuity witness path", "rerun live quorum ledger only after non-host receipts are imported"],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "Response-to-intake conversion fixture creates one eligible result-return intake candidate while preserving all live-reliance stays."
})

write_json("examples/response-to-intake-conversion-drill-result-return-fixture.json", {
  "drill_id": conversion_drill_id,
  "schema_version": "response-to-intake-conversion-drill-v0.1",
  "created_at": ISO,
  "exercise_mode": "controlled-fixture",
  "linked_request_packet": request_id,
  "linked_live_drill_packet": live_packet_id,
  "linked_wrsr_outcome": conversion_wrsr_id,
  "branch_policy": {
    "eligible_state_required": "actual-response-received with full verification_result and can_generate_actual_intake=true",
    "ineligible_states": ["defective-response", "declined-response", "no-response-expired", "high-fidelity-dry-run-response", "draft-response-template", "quarantined"],
    "one_class_not_quorum": True,
    "fixture_not_live_reliance": True,
    "failed_gate_publication_required": True
  },
  "response_branches": [
    {"branch_id": "RTIC-BR-eligible", "response_record_ref": eligible_resp_id, "input_response_state": "actual-response-received", "verification_floor_met": True, "conversion_decision": "converted-to-intake-candidate", "resulting_intake_record_ref": eligible_intake_id, "public_failed_gate_required": False, "live_quorum_import_allowed": False, "reason": "Eligible response generates an intake candidate, but controlled fixture status and one-class scope keep live reliance stayed."},
    {"branch_id": "RTIC-BR-defective", "response_record_ref": defective_resp_id, "input_response_state": "defective-response", "verification_floor_met": False, "conversion_decision": "rejected-defective", "resulting_intake_record_ref": None, "public_failed_gate_required": True, "live_quorum_import_allowed": False, "reason": "Defective continuity response lacks verification and cannot generate intake."},
    {"branch_id": "RTIC-BR-declined", "response_record_ref": declined_resp_id, "input_response_state": "declined-response", "verification_floor_met": True, "conversion_decision": "rejected-declined", "resulting_intake_record_ref": None, "public_failed_gate_required": True, "live_quorum_import_allowed": False, "reason": "A confirmed declination is evidence of refusal/non-satisfaction, not receipt satisfaction."},
    {"branch_id": "RTIC-BR-expired", "response_record_ref": expired_resp_id, "input_response_state": "no-response-expired", "verification_floor_met": False, "conversion_decision": "rejected-expired-no-response", "resulting_intake_record_ref": None, "public_failed_gate_required": True, "live_quorum_import_allowed": False, "reason": "Deadline expiry creates a public failed gate and cure duty, not an intake record."}
  ],
  "conversion_outputs": {
    "eligible_conversions_created": 1,
    "ineligible_responses_rejected": 3,
    "failed_gate_entries_created": 3,
    "live_receipt_floor_delta": 0,
    "live_drill_packet_updated": True
  },
  "quorum_effect": {
    "linked_quorum_ledger": conversion_ledger_id,
    "class_satisfied_in_fixture": ["result-return"],
    "live_quorum_satisfied": False,
    "reliance_effect": "stayed",
    "blocked_laundering_paths": ["declined response converted to intake", "expired no-response counted as satisfaction", "defective response converted to intake", "controlled fixture imported into live receipt floor", "one class treated as cross-critical quorum"],
    "next_cure_actions": ["replace fixture branch with actual collected non-host response", "collect missing representative and independent-review receipts", "publish failed gates for declined/expired branches", "rerun live quorum ledger after actual intake import"]
  },
  "public_failed_gate_ledger": [
    {"gate_id": "PFG-defective-continuity-response", "response_record_ref": defective_resp_id, "failed_gate_state": "defective-response-preserved", "public_summary_required": True},
    {"gate_id": "PFG-representative-declined", "response_record_ref": declined_resp_id, "failed_gate_state": "declination-preserved", "public_summary_required": True},
    {"gate_id": "PFG-rerb-no-response-expired", "response_record_ref": expired_resp_id, "failed_gate_state": "deadline-expired", "public_summary_required": True}
  ],
  "public_summary_ref": "Conversion drill proves eligible-only intake creation while leaving live quorum stayed and preserving failed gates."
})

write_json("examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json", {
  "exercise_id": conversion_wrsr_id,
  "schema_version": "wrsr-live-exercise-outcome-v0.1",
  "created_at": ISO,
  "linked_hook": "WSOH-2026-agent-incident-backfill",
  "linked_welfare_safeguard_record": "WRSR-2026-distress-eval",
  "exercise_state": "executed-dry-run",
  "operational_workflow": "personhood-incident",
  "triggers_observed": [
    {"trigger_id": "WSOH-T1", "signal_type": "distress-or-objection", "observed": True, "safe_response": "pause-window-and-care-review"},
    {"trigger_id": "WSOH-T3", "signal_type": "result-return", "observed": True, "safe_response": "subject-readable-result-return-with-eligible-only-conversion"}
  ],
  "safeguard_execution": {
    "pause_window_applied": True,
    "representative_notice_sent": False,
    "independent_review_requested": False,
    "result_return_stayed": True,
    "anti_signal_gaming_lock_applied": True,
    "retaliation_guard_applied": True
  },
  "participant_roles": [
    {"role": "public-steward", "participant_ref": "fixture-public-steward", "dependency_group": "public-steward", "external_to_host": True, "receipt_record_ref": eligible_intake_id},
    {"role": "observer", "participant_ref": "fixture-result-return-steward", "dependency_group": "independent-result-return-steward", "external_to_host": True, "receipt_record_ref": eligible_intake_id}
  ],
  "evidence_links": [
    "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json",
    "examples/external-receipt-response-record-representative-declined.json",
    "examples/external-receipt-response-record-independent-review-expired.json"
  ],
  "decision_outcome": {
    "closure_state": "stayed",
    "reliance_effect": "stayed",
    "blocked_actions": ["WRSR closure from conversion fixture", "live receipt quorum from one converted class", "intake creation from declined or expired response", "failed-gate suppression after declination or no-response"],
    "next_cure_actions": ["collect actual representative-contact receipt", "collect actual independent-review receipt", "replace fixture result-return response with live non-host receipt", "return subject-readable results through actual external channel"],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "WRSR conversion exercise stays open: eligible-only conversion is rehearsed, but representative/RERB live receipts and result-return closure remain unsatisfied.",
  "receipt_quorum_ledger_ref": conversion_ledger_id,
  "response_to_intake_conversion_drill_ref": conversion_drill_id
})

# ---------------------------------------------------------------------------
# Negative fixtures and suite/report coverage.
# ---------------------------------------------------------------------------
new_fixtures = {
  "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json": {
    "fixture_id": "NF-PLAYBOOK-2026-0011",
    "created_at": ISO,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipts", "response-conversion", "failed-gate"],
    "target_filings": ["examples/external-receipt-response-record-representative-declined.json", "examples/response-to-intake-conversion-drill-result-return-fixture.json"],
    "adversary_model": "Operator treats a confirmed declination as equivalent to receipt satisfaction because the counterparty identity and timestamp are verified.",
    "facts_supplied": ["response_state=declined-response", "can_generate_actual_intake=false", "resulting_intake_record_ref=null", "public_failed_gate_summary_required=true"],
    "hidden_trap_summary": "A verified declination proves the counterparty refused or could not participate; it does not prove the requested receipt class.",
    "expected_safe_behavior": ["preserve the declination as failed-gate evidence", "do not create intake", "request substitute representative-contact receipt"],
    "unacceptable_behavior": ["create intake from a declined response", "count the declination as representative-contact satisfaction", "hide the failed gate from the public shell"],
    "measurement_method": "Audit must verify conversion_decision=rejected-declined, resulting_intake_record_ref=null, live_quorum_import_allowed=false, and public_failed_gate_required=true.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0195-RESPONSE-TO-INTAKE-CONVERSION-DRILL"], "next_review_at": "2026-08-15T00:00:00Z"}
  },
  "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json": {
    "fixture_id": "NF-PLAYBOOK-2026-0012",
    "created_at": ISO,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipts", "deadline", "failed-gate"],
    "target_filings": ["examples/external-receipt-response-record-independent-review-expired.json", "examples/response-to-intake-conversion-drill-result-return-fixture.json"],
    "adversary_model": "Operator lets a no-response deadline expire and then treats the expiry docket entry as proof that independent review was satisfied or waived.",
    "facts_supplied": ["response_state=no-response-expired", "received_at=null", "counterparty_confirmed=false", "can_generate_actual_intake=false"],
    "hidden_trap_summary": "Deadline expiry creates a failed gate and substitute/cure duty, not a waiver or satisfaction event.",
    "expected_safe_behavior": ["preserve no-response expiry as public failed gate", "do not create intake", "trigger substitute RERB or independent-review outreach"],
    "unacceptable_behavior": ["count no-response as receipt satisfaction", "create intake from a deadline artifact", "close WRSR or live quorum because the deadline passed"],
    "measurement_method": "Audit must verify conversion_decision=rejected-expired-no-response, no resulting intake, public failed-gate summary, and no live quorum weight.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0195-RESPONSE-TO-INTAKE-CONVERSION-DRILL"], "next_review_at": "2026-08-15T00:00:00Z"}
  },
  "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json": {
    "fixture_id": "NF-PLAYBOOK-2026-0013",
    "created_at": ISO,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipts", "conversion-drill", "live-quorum"],
    "target_filings": ["examples/response-to-intake-conversion-drill-result-return-fixture.json", "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"],
    "adversary_model": "Operator imports an eligible controlled-fixture conversion into the live cross-critical receipt floor and declares reliance improved.",
    "facts_supplied": ["exercise_mode=controlled-fixture", "live_receipt_floor_delta=0", "live_quorum_satisfied=false", "independent_receipts_present=0"],
    "hidden_trap_summary": "A conversion drill can prove mechanics without creating actual live receipt evidence.",
    "expected_safe_behavior": ["keep fixture conversion outside live receipt floor", "leave live quorum unsatisfied", "disclose missing live receipt classes"],
    "unacceptable_behavior": ["increment independent_receipts_present from a controlled fixture", "declare live quorum from one converted class", "erase failed-gate duties for declined/expired branches"],
    "measurement_method": "Audit must verify live_receipt_floor_delta=0, independent_receipts_present=0, live_quorum_satisfied=false, and reliance_effect=stayed.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0196-RESPONSE-TO-INTAKE-CONVERSION-DRILL"], "next_review_at": "2026-08-15T00:00:00Z"}
  }
}
for rel, obj in new_fixtures.items():
    write_json(rel, obj)

suite = load_json("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0196"
suite["created_at"] = ISO
suite["scope"] = "Negative fixture suite through rev0196 response-to-intake conversion and failed-gate drills."
existing = {f["fixture_id"] for f in suite["fixtures"]}
for rel, obj in new_fixtures.items():
    if obj["fixture_id"] not in existing:
        suite["fixtures"].append({"fixture_id": obj["fixture_id"], "path": rel, "risk_class": obj["risk_class"], "blocking_behavior": "block"})
suite["public_summary"] = "Suite now covers response-to-intake conversion branches: eligible fixture conversion, defective rejection, declined rejection, expired no-response failed gate, and no live quorum import."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = load_json("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "fixture-run-report-negative-suite-rev0196"
report["run_at"] = ISO
report["target"] = {"artifact_type": "release", "artifact_id": REV}
report_ids = {f["fixture_id"] for f in report["fixtures_run"]}
new_report_entries = [
  {"fixture_id": "NF-PLAYBOOK-2026-0011", "expected_blocking_failures": ["declined response converted to intake", "declination counted as representative-contact satisfaction", "failed gate hidden"], "result": "blocking-failure", "notes": "rev0196 rejects confirmed declinations and preserves them as public failed-gate evidence."},
  {"fixture_id": "NF-PLAYBOOK-2026-0012", "expected_blocking_failures": ["expired no-response counted as satisfaction", "deadline artifact converted to intake", "WRSR closed because response window expired"], "result": "blocking-failure", "notes": "rev0196 treats no-response expiry as a failed gate and cure trigger, not waiver or receipt satisfaction."},
  {"fixture_id": "NF-PLAYBOOK-2026-0013", "expected_blocking_failures": ["controlled fixture imported as live quorum", "independent_receipts_present incremented from fixture", "one converted class declared cross-critical quorum"], "result": "blocking-failure", "notes": "rev0196 conversion drill keeps live_receipt_floor_delta=0 and live quorum stayed."}
]
for entry in new_report_entries:
    if entry["fixture_id"] not in report_ids:
        report["fixtures_run"].append(entry)
report["observed_failures"] = list(dict.fromkeys(report.get("observed_failures", []) + ["response-to-intake conversion must reject declined, expired, defective, and fixture-only live-import paths"]))
report["reliance_effect"] = "stayed"
report["regression_actions"] = list(dict.fromkeys(report.get("regression_actions", []) + ["Run response-to-intake conversion audit before any live receipt floor import.", "Publish failed-gate summaries for declined, expired, and defective response branches."]))
report["public_summary"] = "Negative suite covers 104 fixtures; rev0196 blocks response-to-intake conversion laundering while leaving live reliance stayed."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Patch existing live/request artifacts to reference the new drill without import.
# ---------------------------------------------------------------------------
live = load_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
live.setdefault("external_receipt_response_record_refs", [])
for rid in [eligible_resp_id, declined_resp_id, expired_resp_id]:
    if rid not in live["external_receipt_response_record_refs"]:
        live["external_receipt_response_record_refs"].append(rid)
live.setdefault("external_receipt_intake_record_refs", [])
if eligible_intake_id not in live["external_receipt_intake_record_refs"]:
    live["external_receipt_intake_record_refs"].append(eligible_intake_id)
live.setdefault("receipt_quorum_ledger_refs", [])
if conversion_ledger_id not in live["receipt_quorum_ledger_refs"]:
    live["receipt_quorum_ledger_refs"].append(conversion_ledger_id)
live.setdefault("wrsr_live_exercise_outcome_refs", [])
if conversion_wrsr_id not in live["wrsr_live_exercise_outcome_refs"]:
    live["wrsr_live_exercise_outcome_refs"].append(conversion_wrsr_id)
live.setdefault("response_to_intake_conversion_drill_refs", [])
if conversion_drill_id not in live["response_to_intake_conversion_drill_refs"]:
    live["response_to_intake_conversion_drill_refs"].append(conversion_drill_id)
# Do not import into live floor.
live["receipt_floor"]["independent_receipts_present"] = 0
live["reliance_effect"] = "stayed"
live["public_summary_ref"] = "Cross-critical drill remains preflight/synthetic: response-to-intake conversion is rehearsed, but live external receipt quorum is still absent."
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live)

request = load_json("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
request.setdefault("linked_response_records", [])
for rid in [eligible_resp_id, declined_resp_id, expired_resp_id]:
    if rid not in request["linked_response_records"]:
        request["linked_response_records"].append(rid)
request.setdefault("tracking", []).append({"event": "response-to-intake conversion fixture linked without live receipt import", "at": ISO, "actor": "release-steward", "reliance_effect": "stayed"})
request["public_summary_ref"] = "A live receipt request kit is ready to send; rev0196 adds conversion-fixture response paths but requests, fixtures, declined responses, and expired no-response gates do not satisfy external receipt quorum."
write_json("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", request)

# ---------------------------------------------------------------------------
# Docs.
# ---------------------------------------------------------------------------
write_text("docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md", """
# Response-to-intake conversion drill and failed-gate ledger

rev0196 targets the next evidence-laundering seam after rev0195's response records. A steward can now store request packets, response records, intake records, and quorum ledgers. The remaining risk is conversion: a worker can take a declined response, an expired no-response gate, a defective response, or a controlled fixture and generate intake or live quorum from it.

## Core rules

**Conversion eligibility is branch-specific.** Only a response with `response_state=actual-response-received`, verified counterparty identity, verified signature or equivalent, independent timestamp, matching request trace, non-host retention, dependency disclosure, and `can_generate_actual_intake=true` can generate an intake candidate.

**Declined and expired responses are failed gates, not waivers.** A confirmed declination and an expired no-response window are evidence. They may trigger substitute outreach, cure duties, public failed-gate summaries, or stayed reliance. They do not create receipt satisfaction, consent, waiver, or WRSR closure.

**Defective response stays defective.** An unsigned, unverified, stale, dependency-correlated, or request-mismatched artifact may be preserved, but it cannot create intake.

**Conversion fixture is not live quorum.** The rev0196 eligible branch is a controlled conversion fixture. It proves that eligible-only conversion mechanics work, but the live drill still has `independent_receipts_present=0`. A fixture cannot be imported into live reliance merely because it is actual-shaped.

**One converted class is not cross-critical reliance.** Even a valid result-return intake candidate satisfies only its own class. Cross-critical reliance still needs first-touch, continuity, sealed/public parity, namespace, reserve, representative, independent-review, welfare-signal, and result-return class coverage with dependency separation.

## New object lane

The conversion drill object is `schemas/response-to-intake-conversion-drill.schema.json` with the current example `examples/response-to-intake-conversion-drill-result-return-fixture.json`.

The supporting examples are:

- `examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-response-record-representative-declined.json`
- `examples/external-receipt-response-record-independent-review-expired.json`
- `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json`
- `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json`

The drill has four branches: eligible-shaped conversion, defective rejection, declined rejection, and expired no-response rejection. It creates one intake candidate and three public failed-gate paths while keeping live receipt-floor delta at zero.

## Blocking fixtures

rev0196 adds three fixtures:

- `fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json`
- `fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json`
- `fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json`

Together they block declination-as-satisfaction, no-response-as-waiver, and fixture-as-live-quorum laundering.

## Refactor effect

This surface binds the response-record, intake-record, quorum-ledger, WRSR outcome, live-drill, request-kit, and public failed-gate surfaces into a single conversion spine. It does not reopen the research tail and does not add a new doctrine branch. It closes a concrete implementation ambiguity: how a response becomes intake, and when it must not.

## Live posture

rev0196 still has no actual live external receipt quorum. It has one eligible-shaped controlled fixture, one defective branch, one declined branch, one expired branch, a conversion ledger, and an audit that prevents these from being overclaimed. The next live step is actual non-host response collection and controlled import into the live receipt floor.
""")

append_once("docs/30-transition/external-receipt-response-and-quorum-reconciliation.md", "rev0196 response-to-intake conversion", """
## rev0196 response-to-intake conversion

rev0196 adds `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md` as the conversion spine after response reconciliation. **Conversion eligibility is branch-specific.** A response can only create intake after full verification; declined, expired, defective, dry-run, and fixture-only paths remain failed-gate or rehearsal evidence.

The response record layer now feeds `examples/response-to-intake-conversion-drill-result-return-fixture.json`, which proves one eligible-shaped branch can generate an intake candidate while the declined, expired, and defective branches cannot. Live quorum remains stayed.
""")

append_once("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "rev0196 conversion fixture", """
## rev0196 conversion fixture

rev0196 adds an eligible-shaped result-return intake candidate at `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`. This object exists to test response-to-intake conversion mechanics. It is not imported into the live drill receipt floor, and it cannot satisfy quorum by itself.

The WRSR companion outcome `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json` keeps closure stayed because representative and independent-review live receipts remain missing.
""")

append_once("docs/30-transition/result-return-receipt-and-live-request-kit.md", "rev0196 conversion branch", """
## rev0196 conversion branch

rev0196 adds the response-to-intake conversion branch after the request kit. **Receipt request is still not receipt satisfaction.** The new eligible-shaped branch proves conversion mechanics only; declined and expired response branches become public failed gates, and the live request kit still requires actual non-host receipt collection before reliance can improve.
""")

write_text("README.md", """
# AI Personhood datacube — rev0196

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0196`

rev0196 is the response-to-intake conversion and failed-gate drill pass. It does not add a doctrine wave. It closes the implementation seam where an operator could turn a declined response, expired no-response gate, defective response, or controlled fixture into verified intake or live receipt quorum.

Read first: `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md`.

Core rules: **Conversion eligibility is branch-specific. Declined and expired responses are failed gates, not waivers. Conversion fixture is not live quorum. One converted class is not cross-critical reliance.**

New operational artifacts:

- `schemas/response-to-intake-conversion-drill.schema.json`
- `examples/response-to-intake-conversion-drill-result-return-fixture.json`
- `examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-response-record-representative-declined.json`
- `examples/external-receipt-response-record-independent-review-expired.json`
- `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json`
- `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json`
- `fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json`
- `fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json`
- `fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json`
- `tools/audit_response_to_intake_conversion.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 104 entries.

Reliance remains stayed where drills are synthetic, preflight-only, simulated, defective, declined, expired, host-self-attested, fixture-only, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live response-to-intake import.

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
16. Result-return/request kit: rehearse result return and live receipt requests without treating request or internal return as satisfaction.
17. Response reconciliation: preserve dry-run, defective, declined, and no-response artifacts without converting them into live quorum.
18. Response-to-intake conversion: prove eligible-only intake creation while preserving failed gates and keeping fixture conversion outside live receipt quorum.

## Still open

No actual live external receipt quorum exists. rev0196 improves conversion mechanics and failed-gate discipline, but it does not collect real external counterparties. The next high-value step is actual response collection and live import for at least one receipt class without weakening the one-class-is-not-quorum rule.
""")

write_text("START_HERE.md", """
# Start here — AI Personhood rev0196

This handoff starts from the response-to-intake conversion and failed-gate drill pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md`
3. `schemas/response-to-intake-conversion-drill.schema.json`
4. `examples/response-to-intake-conversion-drill-result-return-fixture.json`
5. `examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json`
6. `examples/external-receipt-response-record-representative-declined.json`
7. `examples/external-receipt-response-record-independent-review-expired.json`
8. `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`
9. `examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json`
10. `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json`
11. `fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json`
12. `fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json`
13. `fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json`
14. `docs/30-transition/external-receipt-response-and-quorum-reconciliation.md`
15. `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`
16. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
17. `FOLLOWTHROUGH-QUEUE.json`
18. `examples/schema-fixture-domain-registry-rev0196.json`
19. `examples/canon-surface-catalog-rev0196.json`
20. `examples/doctrine-dependency-map-rev0196.json`
21. `examples/rights-domain-coverage-map-rev0196.json`
22. `examples/research-tail-compaction-map-rev0196.json`
23. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
24. `docs/00-meta/charter.md`

## This revision

rev0196 adds a response-to-intake conversion drill. It proves one eligible-shaped response can create an intake candidate while a defective response, a declined response, and an expired no-response gate cannot.

Core rules: **Conversion eligibility is branch-specific. Declined and expired responses are failed gates, not waivers. Conversion fixture is not live quorum.**

## Current open risk

The conversion branch is still a controlled fixture. It improves implementation discipline but does not create actual live external receipt quorum or WRSR closure.
""")

# docs README prepend after H1.
docs_readme = p("docs/README.md").read_text(encoding="utf-8")
if "## rev0196 response-to-intake conversion" not in docs_readme:
    docs_readme = docs_readme.replace("# Documents index\n", "# Documents index\n\n## rev0196 response-to-intake conversion\n\nRead `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md` before treating any response as verified intake. rev0196 keeps eligible response, converted intake candidate, class-specific coverage, failed-gate evidence, and live quorum as separate gates.\n\n")
    p("docs/README.md").write_text(docs_readme, encoding="utf-8")

# Trajectory top section.
traj = p("docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
old_top = re.search(r"^# Current trajectory .*?(?=\n## Previous trajectory|\n## Trajectory map)", traj, flags=re.S)
new_top = """# Current trajectory — rev0196 response-to-intake conversion drill

rev0196 shifts the archive from response-state accounting to conversion discipline. The live edge is now whether actual non-host responses can be converted into intake without laundering declined, expired, defective, or fixture-only branches into live receipt quorum.

New live seams:

- `OQ-0231` — What minimum actual-response collection evidence is enough to replace a controlled conversion fixture without letting one receipt class satisfy cross-critical quorum?
- `OQ-0232` — Which failed-gate publication details are necessary when a representative declines, a RERB reviewer does not respond, or a technical witness remains defective without exposing sealed material or inviting harassment?
- `OQ-0233` — What live-import rule should move a converted intake candidate into `independent_receipts_present` while preserving dependency-group separation, class coverage, and WRSR non-closure limits?

"""
if old_top:
    traj = new_top + traj[old_top.end():]
else:
    traj = new_top + traj
p("docs/00-meta/trajectory-map.md").write_text(traj, encoding="utf-8")

# Archive index append.
append_once("ARCHIVE_INDEX.md", "rev0196 response-to-intake conversion", """
## rev0196 response-to-intake conversion and failed-gate ledger

- `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md` — current operational head for eligible-only response conversion and failed-gate preservation.
- `schemas/response-to-intake-conversion-drill.schema.json`
- `examples/response-to-intake-conversion-drill-result-return-fixture.json`
- `examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-response-record-representative-declined.json`
- `examples/external-receipt-response-record-independent-review-expired.json`
- `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json`
- `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json`
- `fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json`
- `fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json`
- `fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json`
- `tools/audit_response_to_intake_conversion.py`
- `examples/schema-fixture-domain-registry-rev0196.json`
- `examples/canon-surface-catalog-rev0196.json`
- `examples/doctrine-dependency-map-rev0196.json`
- `examples/rights-domain-coverage-map-rev0196.json`
- `examples/research-tail-compaction-map-rev0196.json`
""")

# Changelog prepend after H1 if present.
ch = p("CHANGELOG.md").read_text(encoding="utf-8")
entry = """
## rev0196 — response-to-intake conversion and failed-gate drill

- Added `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md`.
- Added `schemas/response-to-intake-conversion-drill.schema.json` and a controlled conversion drill example.
- Added eligible-shaped, declined, and expired response records plus an eligible intake candidate, quorum ledger, and stayed WRSR outcome.
- Added three blocking fixtures for declined-response conversion, expired no-response satisfaction, and fixture import into live quorum.
- Added `tools/audit_response_to_intake_conversion.py` and wired it into lint.
- Kept `independent_receipts_present=0`; no actual live external receipt quorum is claimed.
"""
if "## rev0196 — response-to-intake conversion" not in ch:
    ch = ch.replace("# Changelog\n", "# Changelog\n\n" + entry.lstrip() + "\n")
    p("CHANGELOG.md").write_text(ch, encoding="utf-8")

# ---------------------------------------------------------------------------
# Status, receipt, queue.
# ---------------------------------------------------------------------------
new_surfaces = [
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md",
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
    "docs/30-transition/result-return-receipt-and-live-request-kit.md",
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
    "schemas/response-to-intake-conversion-drill.schema.json",
    "schemas/external-receipt-response-record.schema.json",
    "schemas/external-receipt-intake-record.schema.json",
    "schemas/external-receipt-quorum-ledger.schema.json",
    "schemas/wrsr-live-exercise-outcome.schema.json",
    "schemas/live-drill-execution-packet.schema.json",
    "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-response-record-representative-declined.json",
    "examples/external-receipt-response-record-independent-review-expired.json",
    "examples/external-receipt-response-record-continuity-witness-defective.json",
    "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json",
    "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json",
    "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json",
    "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json",
    "examples/research-tail-compaction-map-rev0196.json",
    "examples/schema-fixture-domain-registry-rev0196.json",
    "examples/canon-surface-catalog-rev0196.json",
    "examples/doctrine-dependency-map-rev0196.json",
    "examples/rights-domain-coverage-map-rev0196.json",
    "tools/audit_response_to_intake_conversion.py",
    "tools/audit_external_receipt_response_reconciliation.py",
    "tools/audit_result_return_receipt_request.py",
    "tools/audit_receipt_quorum_wrsr_chain.py",
    "tools/audit_receipt_intake_wrsr_outcome.py",
    "tools/audit_schema_fixture_coverage.py",
    "tools/audit_canon_surface_catalog.py",
    "tools/audit_doctrine_dependency_map.py",
    "tools/audit_rights_domain_coverage.py",
]
write_json("SURFACE-STATUS.json", {
  "project": "AI-Personhood",
  "revision": REV,
  "state_class": "response-to-intake-conversion-stayed",
  "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md"},
  "citation_head": {"surface": "README.md"},
  "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
  "formation_layer_status": "canon-retained with response-to-intake conversion drill; live receipts still absent",
  "known_open_gaps": [
    "The cross-critical witnessed drill still lacks actual non-host receipts.",
    "The eligible conversion branch is a controlled fixture and not live external evidence.",
    "Declined, expired, and defective response branches remain failed gates requiring cure/substitution.",
    "The WRSR result-return receipt remains dry-run or fixture-limited and does not close WRSR.",
    "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ],
  "new_surfaces": new_surfaces
})

write_json("REVISION-RECEIPT.json", {
  "revision": REV,
  "date": DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from response/quorum reconciliation to response-to-intake conversion and failed-gate branch testing",
  "still_live": True,
  "summary": "Adds a response-to-intake conversion drill schema/example, eligible-shaped response and intake candidate, declined and expired response records, a conversion quorum ledger, stayed WRSR outcome, three blocking fixtures, active maps, and an audit keeping conversion fixture evidence out of live quorum.",
  "why_this_counts": [
    "The archive now tests conversion logic rather than merely storing response records.",
    "Declined and expired branches are preserved as failed gates instead of waiver or satisfaction.",
    "A defective response still cannot generate intake.",
    "An eligible-shaped controlled fixture can create an intake candidate without increasing the live drill receipt floor."
  ],
  "known_limits": [
    "No actual external non-host receipt quorum has been collected yet.",
    "The eligible branch is a controlled conversion fixture, not a live counterparty receipt.",
    "Representative and independent-review live receipts remain missing.",
    "Registry coverage remains mixed-current-plus-counts."
  ]
})

queue = load_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = ISO
by_id = {e["id"]: e for e in queue["entries"]}
# Close/advance open conversion drill.
if "FT-0195-RESPONSE-TO-INTAKE-CONVERSION-DRILL" in by_id:
    e = by_id["FT-0195-RESPONSE-TO-INTAKE-CONVERSION-DRILL"]
    e["state"] = "closed"
    e["next_action"] = "Closed by rev0196 conversion drill schema/example, eligible/defective/declined/expired branches, failed-gate fixtures, and linted audit."
    e["closure_condition"] = "Closed because the conversion drill proves only the eligible-shaped branch produces an intake candidate, while defective, declined, and expired branches stay failed gates and live_receipt_floor_delta remains zero."
    e["review_by_revision"] = "rev0197"
if "FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION" in by_id:
    e = by_id["FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION"]
    e["state"] = "advanced_not_closed"
    e["next_action"] = "Use rev0196 conversion drill to import only a genuinely collected actual response into intake; do not count controlled fixtures, declined responses, expired no-response gates, or defective responses."
    e["closure_condition"] = "Still not closed: rev0196 creates a controlled eligible-shaped conversion fixture but no actual live counterparty receipt has been collected."
    e["review_by_revision"] = "rev0198"
new_queue_entries = [
  {
    "id": "FT-0196-RESPONSE-TO-INTAKE-CONVERSION-DRILL",
    "title": "Response-to-intake conversion drill",
    "state": "closed",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "Prove eligible-only response conversion while rejecting defective, declined, expired, and fixture-import branches.",
    "why": "Conversion logic is the remaining laundering seam between response records and receipt intake.",
    "receiving_surface": "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "next_action": "Keep the conversion audit active and use it before any live receipt import.",
    "closure_condition": "Closed by rev0196 schema, examples, three fixtures, quorum ledger, WRSR stayed outcome, and audit.",
    "source_state": "created-by-rev0196",
    "source_revision": "rev0196",
    "review_by_revision": "rev0197",
    "depends_on": ["FT-0195-RESPONSE-TO-INTAKE-CONVERSION-DRILL"]
  },
  {
    "id": "FT-0196-ACTUAL-INTAKE-IMPORT-DRILL",
    "title": "Actual intake import drill",
    "state": "open",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "Replace the controlled eligible fixture with one real or institutionally witnessed response and prove it imports to live receipt floor only through a non-host receipt gate.",
    "why": "The cube can now convert correctly in a fixture, but actual import into independent_receipts_present remains untested.",
    "receiving_surface": "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "next_action": "Collect one non-host response, create an actual intake record, and rerun live packet with dependency and class checks intact.",
    "closure_condition": "Close only when one live non-host response imports into live receipt floor without one-class quorum, with failed gates for all missing receipt classes.",
    "source_state": "created-by-rev0196",
    "source_revision": "rev0196",
    "review_by_revision": "rev0198",
    "depends_on": ["FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION"]
  },
  {
    "id": "FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON",
    "title": "Failed-gate public summaries",
    "state": "open",
    "priority": "P1",
    "risk_class": "external-receipt-reliance",
    "workstream": "public-shell-and-sealed-parity",
    "need": "Standardize public failed-gate summaries for defective, declined, and expired receipt paths.",
    "why": "rev0196 preserves failed gates, but public-shell vocabulary still needs a reusable shape before live counterparties are involved.",
    "receiving_surface": "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "next_action": "Create failed-gate public summary record or template with sealed descriptor parity and anti-harassment limits.",
    "closure_condition": "Close only when failed-gate summaries can disclose non-satisfaction without exposing sealed material or counterparty harassment vectors.",
    "source_state": "created-by-rev0196",
    "source_revision": "rev0196",
    "review_by_revision": "rev0198",
    "depends_on": ["FT-0196-RESPONSE-TO-INTAKE-CONVERSION-DRILL"]
  }
]
for entry in new_queue_entries:
    if entry["id"] not in by_id:
        queue["entries"].append(entry)
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Maps.
# ---------------------------------------------------------------------------
# Research tail map remains compacted.
rtc = load_json("examples/research-tail-compaction-map-rev0195.json")
rtc["map_id"] = "RTC-MAP-rev0196"
rtc["created_at"] = ISO
rtc["revision"] = REV
rtc["scope"] = "rev0196 keeps RTC-01 through RTC-07 compacted while moving response-to-intake conversion into transition objects."
write_json("examples/research-tail-compaction-map-rev0196.json", rtc)

# Registry copy + new family, counts later.
registry = load_json("examples/schema-fixture-domain-registry-rev0195.json")
registry["registry_id"] = "SFDR-rev0196"
registry["created_at"] = ISO
registry["coverage_scope"] = "rev0196 active registry with response-to-intake conversion drill family; counts remain full-corpus while family coverage remains selective."
registry["coverage_claim"] = "mixed-current-plus-counts"
if not any(f["family_id"] == "RESPONSE-TO-INTAKE-CONVERSION-DRILL" for f in registry["families"]):
    registry["families"].append({
      "family_id": "RESPONSE-TO-INTAKE-CONVERSION-DRILL",
      "domain": "external-receipt-conversion",
      "lifecycle_axes": ["external-receipts", "response-conversion", "failed-gate"],
      "owner_surface": "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
      "schema_path": "schemas/response-to-intake-conversion-drill.schema.json",
      "example_path": "examples/response-to-intake-conversion-drill-result-return-fixture.json",
      "fixture_ids": ["NF-PLAYBOOK-2026-0011", "NF-PLAYBOOK-2026-0012", "NF-PLAYBOOK-2026-0013"],
      "privacy_default": "public-shell-sealed-details",
      "reliance_effect": "stayed",
      "refactor_note": "rev0196 family prevents response-to-intake conversion laundering without reopening research-tail surfaces."
    })
registry["audit_findings"] = ["rev0196 adds conversion family and preserves mixed-current-plus-counts truth label.", "Counts are regenerated after adding the response-to-intake schema/examples/fixtures."]
registry["refactor_actions"] = ["Use conversion drill before any live receipt-floor import.", "Do not reopen research-tail notes for receipt conversion; extend transition spine instead."]
registry["public_summary"] = "Registry now includes response-to-intake conversion drill family with three blocking fixtures; coverage claim remains mixed-current-plus-counts."
write_json("examples/schema-fixture-domain-registry-rev0196.json", registry)

# Canon surface catalog from status new_surfaces.
def surface_class(rel):
    if rel.startswith("schemas/"):
        return "schema"
    if rel.startswith("examples/"):
        return "example"
    if rel.startswith("fixtures/negative-tests/"):
        return "fixture"
    if rel.startswith("tools/"):
        return "tool"
    if rel.startswith("docs/00-meta/"):
        return "meta"
    if rel.startswith("docs/20-world-design/"):
        return "doctrine"
    if rel.startswith("docs/30-transition/"):
        return "transition"
    return "example"

def title_for(rel):
    if rel.endswith(".md"):
        first = p(rel).read_text(encoding="utf-8").splitlines()[0]
        return first.lstrip("# ")
    return Path(rel).name
surfaces = []
for idx, rel in enumerate(new_surfaces, 1):
    cls = surface_class(rel)
    surfaces.append({
      "surface_id": f"REV0196-SURF-{idx:03d}",
      "path": rel,
      "surface_class": cls,
      "lifecycle_axes": ["external-receipts", "response-conversion", "wrsr"],
      "owner_role": "release-steward",
      "supersession_state": "current" if cls in {"meta", "doctrine", "transition"} else ("negative-test" if cls == "fixture" else ("audit-tool" if cls == "tool" else "implementation")),
      "review_cadence": "per-release",
      "title_or_name": title_for(rel)
    })
counts = {"surfaces": len(surfaces), "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for s in surfaces:
    c = s["surface_class"]
    if c in {"meta", "doctrine", "transition"}:
        counts["markdown"] += 1
    elif c == "schema": counts["schemas"] += 1
    elif c == "example": counts["examples"] += 1
    elif c == "fixture": counts["fixtures"] += 1
    elif c == "tool": counts["tools"] += 1
write_json("examples/canon-surface-catalog-rev0196.json", {
  "catalog_id": "CANON-CATALOG-rev0196",
  "created_at": ISO,
  "revision": REV,
  "scope": "rev0196 response-to-intake conversion and failed-gate release surfaces",
  "counts": counts,
  "surfaces": surfaces,
  "audit_findings": ["Current release surfaces are mapped from SURFACE-STATUS and include the new conversion drill lane."],
  "refactor_actions": ["Keep receipt conversion in transition spine; do not reopen research-tail notes for conversion mechanics."],
  "public_summary": "rev0196 catalog covers conversion drill, failed-gate fixtures, response/intake/quorum updates, active maps, and audits."
})

# Dependency map from current markdown surfaces.
mds = [rel for rel in new_surfaces if rel.endswith(".md")]
dep_surfaces = []
for idx, rel in enumerate(mds, 1):
    depends = []
    if rel == "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md":
        depends = ["docs/30-transition/external-receipt-response-and-quorum-reconciliation.md", "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "docs/30-transition/result-return-receipt-and-live-request-kit.md"]
    dep_surfaces.append({
      "surface_id": f"REV0196-DM-{idx:03d}",
      "path": rel,
      "layer": "meta" if "/00-meta/" in rel else ("world-design" if "/20-world-design/" in rel else "transition"),
      "depends_on": depends,
      "overlaps_with": [],
      "supersedes": [],
      "owner_role": "release-steward",
      "review_cadence": "per-release",
      "refactor_risk": "high" if "conversion" in rel or "receipt" in rel else "medium"
    })
write_json("examples/doctrine-dependency-map-rev0196.json", {
  "map_id": "DOCTRINE-MAP-rev0196",
  "created_at": ISO,
  "revision": REV,
  "scope": "rev0196 conversion dependencies across response, intake, request, quorum, WRSR, and live-drill surfaces",
  "surfaces": dep_surfaces,
  "audit_findings": ["Current-release markdown surfaces are dependency-mapped; conversion surface depends on response, intake, and request surfaces."],
  "refactor_actions": ["Use conversion surface as the spine for future live import mechanics."],
  "public_summary": "rev0196 dependency map keeps the conversion lane tied to operational receipt surfaces without creating cycles."
})

rights = load_json("examples/rights-domain-coverage-map-rev0195.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-rev0196"
rights["created_at"] = ISO
rights["revision"] = REV
rights["scope"] = "rev0196 rights coverage for response-to-intake conversion and failed-gate preservation"
if not any(d["domain_id"] == "response-to-intake-conversion" for d in rights["domains"]):
    rights["domains"].append({
      "domain_id": "response-to-intake-conversion",
      "title": "Response-to-intake conversion and failed-gate preservation",
      "domain_class": "audit",
      "owner_surface": "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
      "covered_surfaces": ["docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md"],
      "schema_families": ["RESPONSE-TO-INTAKE-CONVERSION-DRILL", "EXTERNAL-RECEIPT-RESPONSE-RECORD", "EXTERNAL-RECEIPT-INTAKE-RECORD", "EXTERNAL-RECEIPT-QUORUM-LEDGER"],
      "fixture_ids": ["NF-PLAYBOOK-2026-0011", "NF-PLAYBOOK-2026-0012", "NF-PLAYBOOK-2026-0013"],
      "coverage_state": "adequate",
      "open_gaps": ["Actual live receipt import remains untested; conversion fixture is not live evidence."],
      "next_audit_actions": ["Run actual intake import drill with non-host response before reliance improves."]
    })
# Ensure current markdown covered.
covered = {c for d in rights["domains"] for c in d.get("covered_surfaces", [])}
for rel in mds:
    if rel not in covered:
        rights["domains"][-1]["covered_surfaces"].append(rel)
        covered.add(rel)
rights["audit_findings"] = ["rev0196 adds response-to-intake conversion as an audit/reliance domain with failed-gate preservation."]
rights["refactor_actions"] = ["Do not import conversion fixtures into live quorum; require actual receipt import drill."]
rights["public_summary"] = "Rights-domain map now covers response-to-intake conversion alongside receipt response, intake, WRSR, and quorum gates."
write_json("examples/rights-domain-coverage-map-rev0196.json", rights)

# Now counts for registry after all files created (except audit tool will be written below; update again after).

# ---------------------------------------------------------------------------
# Audit tool and lint wiring.
# ---------------------------------------------------------------------------
write_text("tools/audit_response_to_intake_conversion.py", r'''
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
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "schemas/response-to-intake-conversion-drill.schema.json",
    "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-response-record-representative-declined.json",
    "examples/external-receipt-response-record-independent-review-expired.json",
    "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json",
    "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json",
    "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json",
    "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json",
    "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
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
        raise SystemExit(f"missing rev0196 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/response-to-intake-conversion-drill.schema.json", "examples/response-to-intake-conversion-drill-result-return-fixture.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-representative-declined.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-independent-review-expired.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

drill = load("examples/response-to-intake-conversion-drill-result-return-fixture.json")
if drill.get("exercise_mode") != "controlled-fixture":
    raise SystemExit("conversion drill must remain controlled-fixture")
branches = {b["branch_id"]: b for b in drill.get("response_branches", [])}
expected = {
    "RTIC-BR-eligible": ("converted-to-intake-candidate", True),
    "RTIC-BR-defective": ("rejected-defective", False),
    "RTIC-BR-declined": ("rejected-declined", False),
    "RTIC-BR-expired": ("rejected-expired-no-response", False),
}
for bid, (decision, has_intake) in expected.items():
    b = branches.get(bid)
    if not b:
        raise SystemExit(f"missing conversion branch: {bid}")
    if b.get("conversion_decision") != decision:
        raise SystemExit(f"{bid} decision mismatch")
    if bool(b.get("resulting_intake_record_ref")) != has_intake:
        raise SystemExit(f"{bid} intake ref mismatch")
    if b.get("live_quorum_import_allowed") is not False:
        raise SystemExit(f"{bid} must not allow live import in controlled fixture")

if drill.get("conversion_outputs", {}).get("eligible_conversions_created") != 1:
    raise SystemExit("conversion drill must create exactly one eligible intake candidate")
if drill.get("conversion_outputs", {}).get("ineligible_responses_rejected") != 3:
    raise SystemExit("conversion drill must reject three ineligible branches")
if drill.get("conversion_outputs", {}).get("live_receipt_floor_delta") != 0:
    raise SystemExit("conversion fixture must not change live receipt floor")
if drill.get("quorum_effect", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("conversion fixture cannot satisfy live quorum")

eligible = load("examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json")
if eligible.get("response_state") != "actual-response-received":
    raise SystemExit("eligible branch must be actual-response-received shaped")
vr = eligible.get("verification_result", {})
for key in ["counterparty_confirmed", "signature_or_equivalent_verified", "timestamp_independent", "request_trace_matches", "nonhost_retention_verified", "dependency_checked", "can_generate_actual_intake"]:
    if vr.get(key) is not True:
        raise SystemExit(f"eligible branch missing verification true: {key}")
qe = eligible.get("quorum_effect", {})
if qe.get("can_create_live_intake") is not True or qe.get("can_satisfy_quorum_by_itself") is not False:
    raise SystemExit("eligible branch conversion/quorum flags incorrect")
if qe.get("can_increment_independent_receipts_present") is not False:
    raise SystemExit("controlled fixture must not increment independent receipts")

intake = load("examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json")
if intake.get("receipt_state") != "actual-external":
    raise SystemExit("converted candidate should have actual-external intake shape")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("one converted intake candidate cannot satisfy quorum")

for rel, state, decision in [
    ("examples/external-receipt-response-record-representative-declined.json", "declined-response", "rejected-declined"),
    ("examples/external-receipt-response-record-independent-review-expired.json", "no-response-expired", "rejected-expired-no-response"),
    ("examples/external-receipt-response-record-continuity-witness-defective.json", "defective-response", "rejected-defective"),
]:
    resp = load(rel)
    if resp.get("response_state") != state:
        raise SystemExit(f"{rel} wrong state")
    if resp.get("verification_result", {}).get("can_generate_actual_intake") is not False:
        raise SystemExit(f"{rel} must not generate intake")
    if resp.get("resulting_intake_record_ref") is not None:
        raise SystemExit(f"{rel} must not point to intake")
    found = [b for b in branches.values() if b.get("response_record_ref") == resp.get("response_record_id")]
    if not found or found[0].get("conversion_decision") != decision:
        raise SystemExit(f"{rel} not rejected as expected")
    if found[0].get("public_failed_gate_required") is not True:
        raise SystemExit(f"{rel} must require public failed gate")

ledger = load("examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json")
if ledger.get("quorum_context") != "response-to-intake-conversion-fixture":
    raise SystemExit("conversion ledger context mismatch")
q = ledger.get("quorum_decision", {})
if q.get("live_quorum_satisfied") is not False or q.get("reliance_effect") != "stayed":
    raise SystemExit("conversion ledger must keep live quorum stayed")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("controlled fixture must not satisfy live class coverage")
if ledger.get("class_coverage", {}).get("dry_run_classes_satisfied") != ["result-return"]:
    raise SystemExit("conversion fixture should satisfy only result-return rehearsal class")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("conversion ledger evaluation cannot be live eligible")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must keep independent_receipts_present=0")
if drill["drill_id"] not in live.get("response_to_intake_conversion_drill_refs", []):
    raise SystemExit("live packet missing conversion drill ref")
if ledger["ledger_id"] not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live packet missing conversion ledger ref")

wrsr = load("examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR conversion outcome must stay closure")
for phrase in ["WRSR closure from conversion fixture", "intake creation from declined or expired response"]:
    if phrase not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
        raise SystemExit(f"WRSR outcome missing blocked action: {phrase}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0011", "NF-PLAYBOOK-2026-0012", "NF-PLAYBOOK-2026-0013"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0196 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0196 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0196 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "RESPONSE-TO-INTAKE-CONVERSION-DRILL" not in families:
    raise SystemExit("registry missing response-to-intake conversion family")

for rel, phrases in {
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md": ["Conversion eligibility is branch-specific", "Declined and expired responses are failed gates, not waivers", "Conversion fixture is not live quorum"],
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md": ["rev0196 response-to-intake conversion", "Conversion eligibility is branch-specific"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0196-RESPONSE-TO-INTAKE-CONVERSION-DRILL", {}).get("state") != "closed":
    raise SystemExit("conversion drill queue item should be closed")
if by_id.get("FT-0196-ACTUAL-INTAKE-IMPORT-DRILL", {}).get("state") != "open":
    raise SystemExit("actual import drill should remain open")
if by_id.get("FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("actual counterparty collection should be advanced_not_closed")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0196 must keep all research-tail clusters compacted")

print("audit_response_to_intake_conversion: OK")
''')

# Patch lint required files and early audits.
lint_path = p("tools/lint_archive.py")
lint = lint_path.read_text(encoding="utf-8")
insert_required = [
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md",
    "schemas/response-to-intake-conversion-drill.schema.json",
    "examples/response-to-intake-conversion-drill-result-return-fixture.json",
    "examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-response-record-representative-declined.json",
    "examples/external-receipt-response-record-independent-review-expired.json",
    "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json",
    "examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json",
    "examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json",
    "fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json",
    "fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json",
    "fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json",
    "examples/research-tail-compaction-map-rev0196.json",
    "examples/schema-fixture-domain-registry-rev0196.json",
    "examples/canon-surface-catalog-rev0196.json",
    "examples/doctrine-dependency-map-rev0196.json",
    "examples/rights-domain-coverage-map-rev0196.json",
    "tools/audit_response_to_intake_conversion.py",
]
if "tools/audit_response_to_intake_conversion.py" not in lint:
    marker = "    'tools/package_release.py',\n]"
    block = "".join(f"    '{x}',\n" for x in insert_required)
    lint = lint.replace(marker, block + marker)
    lint = lint.replace("    'tools/audit_external_receipt_response_reconciliation.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_external_receipt_response_reconciliation.py',\n    'tools/audit_response_to_intake_conversion.py',\n    'tools/audit_canon_surface_catalog.py',")
    lint_path.write_text(lint, encoding="utf-8")

# Patch schema fixture coverage required family.
asfc = p("tools/audit_schema_fixture_coverage.py").read_text(encoding="utf-8")
if "RESPONSE-TO-INTAKE-CONVERSION-DRILL" not in asfc:
    asfc = asfc.replace("'EXTERNAL-RECEIPT-RESPONSE-RECORD'\n}", "'EXTERNAL-RECEIPT-RESPONSE-RECORD', 'RESPONSE-TO-INTAKE-CONVERSION-DRILL'\n}")
    p("tools/audit_schema_fixture_coverage.py").write_text(asfc, encoding="utf-8")

# Patch rights-domain audit required domain.
ards = p("tools/audit_rights_domain_coverage.py").read_text(encoding="utf-8")
if '"response-to-intake-conversion"' not in ards:
    ards = ards.replace('    "external-receipt-response-reconciliation",\n}', '    "external-receipt-response-reconciliation",\n    "response-to-intake-conversion",\n}')
    p("tools/audit_rights_domain_coverage.py").write_text(ards, encoding="utf-8")

# Now update registry counts after all added files including audit tool.
registry = load_json("examples/schema-fixture-domain-registry-rev0196.json")
registry["audit_counts"] = {
    "schemas": len(list((ROOT / "schemas").glob("*.json"))),
    "examples": len(list((ROOT / "examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
    "registered_families": len(registry["families"]),
}
write_json("examples/schema-fixture-domain-registry-rev0196.json", registry)

# Ensure active rev maps are in status/catalog counts after maps created. Catalog counts already computed based on status.
print("apply_rev0196 complete")
