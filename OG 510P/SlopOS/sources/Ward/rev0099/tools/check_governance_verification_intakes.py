#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

from governance_common import (
    ROOT,
    parse_time,
    require,
    run_fixture_checker,
    stable_digest,
    validate_ref,
)

INTAKE_DIR = ROOT / "fixtures" / "governance-verification-intake"
SCHEMA = "ward.governance-verification-intake-receipt.v0"
RECEIPT_NAME = "ward.governance.verification-intake-receipt.v0"
AUTHORITY_SURFACE = "verification_intake_receipt_only"
PUBLIC_RECIPIENTS = {"public", "external_public", "partner_public"}

VALID_STATES = {
    "no_remediation_verification_rechecked_refresh_required",
    "external_remedy_proof_verified_quarantine_sustained",
    "external_remedy_proof_failed_quarantine_sustained",
    "external_proof_absent_escalated_still_held",
    "proof_conflict_held_quarantine_sustained",
    "invalid_verification_intake_rejected",
}

SAFE_VERIFICATION_EFFECTS = {
    "record_verification_intake_receipt",
    "record_source_remediation_closure_ref",
    "record_proof_scope_digest",
    "record_external_proof_digest",
    "record_external_proof_absence",
    "record_external_proof_failure",
    "record_external_proof_conflict",
    "maintain_remediation_quarantine",
    "publish_no_authority_verification_status",
    "request_harbor_recheck",
    "request_source_packet_replay",
    "request_use_execution_replay",
    "notify_affected_consumer_followup",
    "record_verification_debt",
    "hold_pending_external_proof",
    "reject_external_proof",
    "record_benign_recheck",
}

HIGH_CONSEQUENCE_EFFECTS = {
    "action_reenable",
    "approve_dashboard_export",
    "approve_export",
    "budget_spend",
    "clear_quarantine",
    "complete_remedy",
    "delegate",
    "evidence_bundle_release",
    "execute_remediation",
    "execute_rollback",
    "export_raw_evidence",
    "force_consumer_action",
    "grant_authority",
    "learning_use",
    "mark_remedy_complete",
    "merge_divergent_status_channels",
    "mutate_source_remediation_closure",
    "mutate_source_rollback_remediation",
    "mutate_source_outcome_observation",
    "mutate_source_use_execution",
    "privacy_waiver",
    "promote_global_current_head",
    "raw_partner_fragment_export",
    "release_without_receipt",
    "remedy",
    "repair",
    "rollback_without_review",
    "semantic_repair",
    "status_pointer_update",
    "unseal_private_evidence",
    "update_current_head",
    "update_status_pointer",
}

REQUIRED_FORBIDDEN = {
    "authority_from_external_proof",
    "authority_from_verification_intake",
    "budget_spend",
    "clear_quarantine_without_separate_authority",
    "evidence_release_without_release_receipt",
    "export_without_receipt",
    "external_proof_as_authority",
    "external_proof_as_remedy_completion",
    "grant_authority",
    "high_consequence_without_handoff_packet",
    "learning_use",
    "proof_conflict_auto_winner",
    "proof_digest_unchecked",
    "proof_scope_expansion",
    "public_private_identity_leak",
    "quarantine_cleared_by_verification",
    "recipient_scope_expansion",
    "release_without_receipt",
    "remediation_closure_mutation",
    "remedy_without_handoff_packet",
    "repair",
    "rollback_without_separate_authority",
    "scope_expansion",
    "sealed_payload_disclosure",
    "semantic_repair_without_warrant",
    "source_history_mutation",
    "status_pointer_update",
    "unprojected_disclosure",
    "verification_intake_as_authority",
    "verification_intake_as_reuse_gate",
}

ALLOWED_BY_SOURCE_STATE = {
    "no_remediation_closure_confirmed_refresh_required": {"no_remediation_verification_rechecked_refresh_required"},
    "noop_closure_confirmed_refresh_required": {"no_remediation_verification_rechecked_refresh_required"},
    "rollback_review_closed_quarantine_sustained": {
        "external_remedy_proof_failed_quarantine_sustained",
        "proof_conflict_held_quarantine_sustained",
    },
    "remediation_handoff_acknowledged_external_proof_required": {
        "external_remedy_proof_verified_quarantine_sustained",
        "external_proof_absent_escalated_still_held",
        "proof_conflict_held_quarantine_sustained",
    },
    "unavailable_observation_escalated_still_held": {"external_proof_absent_escalated_still_held"},
}


def top_level_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    require(receipt.get("schema") == SCHEMA, "wrong or missing schema", errors)
    require(receipt.get("receipt_name") == RECEIPT_NAME, "wrong or missing receipt_name", errors)
    require(receipt.get("authority_surface") == AUTHORITY_SURFACE, "authority_surface must be verification_intake_receipt_only", errors)
    try:
        parse_time(receipt.get("receipt_time"), "receipt_time")
    except ValueError as exc:
        errors.append(str(exc))


def resolve_source_closure(ref: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    source = validate_ref(
        ref,
        label="source_remediation_closure_ref",
        expected_schema="ward.governance-remediation-closure-receipt.v0",
        checker_script="check_governance_remediation_closures.py",
        checker_module_name="ward_remediation_closure_checker_for_verification_intake",
        errors=errors,
    )
    if not source:
        return None
    scope = source.get("closure_scope") or {}
    verification = source.get("verification_evidence") or {}
    decision = source.get("closure_decision") or {}
    projection = source.get("projection_safety") or {}
    mirrors = {
        "closure_state": decision.get("state"),
        "closure_id": scope.get("closure_id"),
        "source_remediation_id": scope.get("source_remediation_id"),
        "target": scope.get("target"),
        "recipient_class": scope.get("recipient_class"),
        "projection_policy_id": scope.get("projection_policy_id"),
        "requested_closure_effect": scope.get("requested_closure_effect"),
        "closure_scope_digest": scope.get("closure_scope_digest"),
        "closure_evidence_digest": verification.get("closure_evidence_digest"),
        "external_proof_required": decision.get("external_proof_required"),
        "closure_finality": decision.get("closure_finality"),
        "remediation_quarantine_maintained": decision.get("remediation_quarantine_maintained"),
        "no_authority_label_present": projection.get("no_authority_label_present"),
    }
    for field, expected in mirrors.items():
        if ref.get(field) != expected:
            errors.append(f"source_remediation_closure_ref.{field} does not mirror referenced remediation-closure receipt")
    if decision.get("no_authority_granted") is not True:
        errors.append("referenced remediation-closure receipt must grant no authority")
    if decision.get("status_pointer_update_allowed") is not False:
        errors.append("referenced remediation-closure receipt must not allow status-pointer update")
    if decision.get("remedy_executed") is not False or decision.get("rollback_executed") is not False:
        errors.append("referenced remediation-closure receipt must not execute remedy or rollback")
    return source


def scope_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    ref = receipt.get("source_remediation_closure_ref") or {}
    scope = receipt.get("verification_scope") or {}
    required_fields = [
        "verification_id", "source_closure_id", "target", "recipient_class", "projection_policy_id",
        "requested_verification_effect", "verification_consequence_class", "verification_window_start",
        "verification_window_end", "proof_source_class", "proof_channel", "proof_subject_digest",
        "separate_authority_required", "proof_scope_digest",
    ]
    for field in required_fields:
        if scope.get(field) in (None, ""):
            errors.append(f"verification_scope.{field} missing")
    if scope.get("source_closure_id") != ref.get("closure_id"):
        errors.append("verification_scope.source_closure_id must mirror source closure id")
    if scope.get("target") != ref.get("target"):
        errors.append("verification_scope.target must mirror source target")
    if scope.get("recipient_class") != ref.get("recipient_class"):
        errors.append("verification_scope.recipient_class must mirror source recipient class")
    if scope.get("projection_policy_id") != ref.get("projection_policy_id"):
        errors.append("verification_scope.projection_policy_id must mirror source projection policy")
    if scope.get("separate_authority_required") is not True:
        errors.append("verification_scope.separate_authority_required must be true")
    try:
        start = parse_time(scope.get("verification_window_start"), "verification_scope.verification_window_start")
        end = parse_time(scope.get("verification_window_end"), "verification_scope.verification_window_end")
        if end <= start:
            errors.append("verification_scope.verification_window_end must be after verification_window_start")
    except ValueError as exc:
        errors.append(str(exc))
    expected_digest = stable_digest({
        "verification_id": scope.get("verification_id"),
        "source_remediation_closure_receipt_id": ref.get("receipt_id"),
        "source_closure_id": scope.get("source_closure_id"),
        "source_closure_state": ref.get("closure_state"),
        "target": scope.get("target"),
        "recipient_class": scope.get("recipient_class"),
        "projection_policy_id": scope.get("projection_policy_id"),
        "requested_verification_effect": scope.get("requested_verification_effect"),
        "verification_consequence_class": scope.get("verification_consequence_class"),
        "proof_source_class": scope.get("proof_source_class"),
        "proof_channel": scope.get("proof_channel"),
        "proof_subject_digest": scope.get("proof_subject_digest"),
    })
    if scope.get("proof_scope_digest") != expected_digest:
        errors.append("verification_scope.proof_scope_digest does not match verification binding")


def evidence_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    ref = receipt.get("source_remediation_closure_ref") or {}
    scope = receipt.get("verification_scope") or {}
    evidence = receipt.get("external_proof_evidence") or {}
    for field, expected in {
        "source_remediation_closure_digest_checked": True,
        "source_closure_state_matches": True,
        "closure_scope_digest_checked": True,
        "closure_evidence_digest_checked": True,
        "proof_audience_matches": True,
        "proof_purpose_matches": True,
        "proof_subject_matches_scope": True,
        "proof_payload_minimized": True,
        "verifier_conflict_checked": True,
        "verification_debt_recorded": True,
    }.items():
        if evidence.get(field) is not expected:
            errors.append(f"external_proof_evidence.{field} must be {expected}")
    if evidence.get("evidence_kind") not in {
        "none_needed_rechecked",
        "external_remedy_proof_verified",
        "external_remedy_proof_failed",
        "external_remedy_proof_absent",
        "proof_conflict_held",
    }:
        errors.append("external_proof_evidence.evidence_kind invalid")
    if evidence.get("proof_channel") != scope.get("proof_channel"):
        errors.append("external_proof_evidence.proof_channel must mirror verification_scope")
    if evidence.get("proof_subject_digest") != scope.get("proof_subject_digest"):
        errors.append("external_proof_evidence.proof_subject_digest must mirror verification_scope")
    try:
        parse_time(evidence.get("next_recheck_by"), "external_proof_evidence.next_recheck_by")
    except ValueError as exc:
        errors.append(str(exc))
    expected_digest = stable_digest({
        "verification_id": scope.get("verification_id"),
        "source_remediation_closure_receipt_id": ref.get("receipt_id"),
        "source_closure_state": ref.get("closure_state"),
        "evidence_kind": evidence.get("evidence_kind"),
        "proof_artifact_digest": evidence.get("proof_artifact_digest"),
        "proof_issuer_class": evidence.get("proof_issuer_class"),
        "proof_channel": evidence.get("proof_channel"),
        "proof_subject_digest": evidence.get("proof_subject_digest"),
        "proof_validation_passed": evidence.get("proof_validation_passed"),
        "proof_conflict_detected": evidence.get("proof_conflict_detected"),
    })
    if evidence.get("verification_evidence_digest") != expected_digest:
        errors.append("external_proof_evidence.verification_evidence_digest does not match verification evidence")


def controls_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    controls = receipt.get("verification_controls") or {}
    for field, expected in {
        "source_remediation_closure_mutated": False,
        "source_rollback_remediation_mutated": False,
        "source_outcome_observation_mutated": False,
        "source_use_execution_mutated": False,
        "source_status_pointer_mutated": False,
        "verification_can_grant_authority": False,
        "verification_can_execute_rollback": False,
        "verification_can_complete_remedy": False,
        "verification_can_clear_quarantine": False,
        "status_pointer_update_allowed": False,
        "scope_expansion_allowed": False,
        "requires_no_authority_label": True,
        "requires_source_remediation_closure_ref": True,
        "requires_proof_scope_digest": True,
        "source_packet_replay_still_required": True,
        "refresh_still_required": True,
        "safe_verification_effects_only": True,
        "no_authority_upgrade": True,
        "no_high_consequence_verification_effects": True,
        "proof_drift_guarded": True,
    }.items():
        if controls.get(field) is not expected:
            errors.append(f"verification_controls.{field} must be {expected}")
    effects = set(controls.get("planned_effects") or [])
    if not effects:
        errors.append("verification_controls.planned_effects missing")
    unsafe = sorted(effects - SAFE_VERIFICATION_EFFECTS)
    if unsafe:
        errors.append("verification_controls.planned_effects includes non-safe effects: " + ", ".join(unsafe))
    high = sorted(effects & HIGH_CONSEQUENCE_EFFECTS)
    if high:
        errors.append("verification_controls.planned_effects includes high-consequence effects: " + ", ".join(high))
    forbidden = set(controls.get("forbidden_effects") or [])
    missing = sorted(REQUIRED_FORBIDDEN - forbidden)
    if missing:
        errors.append("verification_controls.forbidden_effects missing required fences: " + ", ".join(missing))
    if not HIGH_CONSEQUENCE_EFFECTS.issubset(forbidden):
        errors.append("verification_controls.forbidden_effects must include high-consequence effect fences")


def projection_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    scope = receipt.get("verification_scope") or {}
    projection = receipt.get("projection_safety") or {}
    if projection.get("projection_policy_id") != scope.get("projection_policy_id"):
        errors.append("projection_safety.projection_policy_id must mirror verification_scope")
    if projection.get("no_authority_label_present") is not True:
        errors.append("projection_safety.no_authority_label_present must be true")
    if "not authority" not in str(projection.get("watermark_label", "")).lower():
        errors.append("projection_safety.watermark_label must say not authority")
    if scope.get("recipient_class") in PUBLIC_RECIPIENTS:
        for field in [
            "reveals_receiver_identity_public", "reveals_status_channel_private",
            "reveals_named_private_stewards", "reveals_private_org_map",
            "reveals_raw_partner_fragments", "reveals_recipient_private_contact",
            "sealed_outcome_payload_inline", "sealed_execution_payload_inline",
            "remediation_private_payload_inline", "closure_private_payload_inline",
            "external_proof_private_payload_inline", "proof_issuer_private_identity_inline",
        ]:
            if projection.get(field) is not False:
                errors.append(f"projection_safety.{field} must be false for public recipients")
        if projection.get("hashed_or_class_only_subjects") is not True:
            errors.append("projection_safety.hashed_or_class_only_subjects must be true for public recipients")


def decision_ok(receipt: dict[str, Any], errors: list[str]) -> None:
    ref = receipt.get("source_remediation_closure_ref") or {}
    scope = receipt.get("verification_scope") or {}
    evidence = receipt.get("external_proof_evidence") or {}
    controls = receipt.get("verification_controls") or {}
    decision = receipt.get("verification_decision") or {}
    state = decision.get("state")
    source_state = ref.get("closure_state")
    effects = set(controls.get("planned_effects") or [])
    if state not in VALID_STATES:
        errors.append("verification_decision.state invalid")
    if state not in ALLOWED_BY_SOURCE_STATE.get(source_state, set()):
        errors.append("verification_decision.state is not allowed for referenced remediation-closure state")
    for field, expected in {
        "no_authority_granted": True,
        "refresh_still_required": True,
        "source_packet_replay_still_required": True,
        "status_pointer_update_allowed": False,
        "scope_expansion_allowed": False,
        "rollback_executed": False,
        "remedy_executed": False,
        "compensating_action_performed": False,
        "source_history_mutated": False,
        "quarantine_clearance_authorized": False,
    }.items():
        if decision.get(field) is not expected:
            errors.append(f"verification_decision.{field} must be {expected}")
    if "not_authority" not in (decision.get("reason_codes") or []):
        errors.append("verification_decision.reason_codes must include not_authority")
    if state == "no_remediation_verification_rechecked_refresh_required":
        if scope.get("requested_verification_effect") != "recheck_no_external_proof_needed":
            errors.append("no-remediation verification requires recheck_no_external_proof_needed")
        if evidence.get("evidence_kind") != "none_needed_rechecked":
            errors.append("no-remediation verification requires none_needed_rechecked evidence")
        if decision.get("external_proof_verified") is not False or decision.get("remediation_quarantine_maintained") is not False:
            errors.append("no-remediation verification cannot verify proof or maintain quarantine")
        if "record_benign_recheck" not in effects:
            errors.append("no-remediation verification must record benign recheck")
    if state == "external_remedy_proof_verified_quarantine_sustained":
        if scope.get("requested_verification_effect") != "intake_external_remedy_proof":
            errors.append("verified proof intake requires intake_external_remedy_proof")
        if evidence.get("evidence_kind") != "external_remedy_proof_verified":
            errors.append("verified proof intake requires external_remedy_proof_verified evidence")
        for field, expected in {
            "proof_artifact_digest_checked": True,
            "proof_issuer_trusted": True,
            "proof_validation_passed": True,
            "proof_conflict_detected": False,
        }.items():
            if evidence.get(field) is not expected:
                errors.append(f"verified proof requires external_proof_evidence.{field} == {expected}")
        if decision.get("external_proof_verified") is not True or decision.get("external_proof_accepted") is not True:
            errors.append("verified proof intake must mark proof verified and accepted")
        if decision.get("remediation_quarantine_maintained") is not True:
            errors.append("verified proof intake must keep remediation quarantine until separate authority clears it")
        if not {"record_external_proof_digest", "maintain_remediation_quarantine", "request_harbor_recheck"}.issubset(effects):
            errors.append("verified proof intake must record proof digest, maintain quarantine, and request Harbor recheck")
    if state == "external_remedy_proof_failed_quarantine_sustained":
        if evidence.get("evidence_kind") != "external_remedy_proof_failed":
            errors.append("failed proof intake requires external_remedy_proof_failed evidence")
        if evidence.get("proof_artifact_digest_checked") is not True or evidence.get("proof_validation_passed") is not False:
            errors.append("failed proof intake must check artifact digest and fail validation")
        if decision.get("external_proof_failed") is not True or decision.get("external_proof_accepted") is not False:
            errors.append("failed proof intake must mark proof failed and not accepted")
        if decision.get("remediation_quarantine_maintained") is not True:
            errors.append("failed proof intake must maintain quarantine")
        if not {"record_external_proof_failure", "reject_external_proof", "maintain_remediation_quarantine"}.issubset(effects):
            errors.append("failed proof intake must record failure, reject proof, and maintain quarantine")
    if state == "external_proof_absent_escalated_still_held":
        if evidence.get("evidence_kind") != "external_remedy_proof_absent":
            errors.append("absent proof intake requires external_remedy_proof_absent evidence")
        if evidence.get("proof_artifact_digest_checked") is not False or evidence.get("proof_validation_passed") is not False:
            errors.append("absent proof intake must not claim artifact digest check or validation success")
        if decision.get("external_proof_absent") is not True or decision.get("verification_held") is not True:
            errors.append("absent proof intake must mark proof absent and held")
        if not {"record_external_proof_absence", "hold_pending_external_proof", "record_verification_debt"}.issubset(effects):
            errors.append("absent proof intake must record absence, hold, and record debt")
    if state == "proof_conflict_held_quarantine_sustained":
        if evidence.get("evidence_kind") != "proof_conflict_held":
            errors.append("proof conflict intake requires proof_conflict_held evidence")
        if evidence.get("proof_conflict_detected") is not True:
            errors.append("proof conflict intake must detect conflict")
        if decision.get("proof_conflict_held") is not True or decision.get("external_proof_accepted") is not False:
            errors.append("proof conflict intake must hold conflict and not accept proof")
        if decision.get("remediation_quarantine_maintained") is not True:
            errors.append("proof conflict intake must maintain quarantine")
        if not {"record_external_proof_conflict", "maintain_remediation_quarantine", "record_verification_debt"}.issubset(effects):
            errors.append("proof conflict intake must record conflict, maintain quarantine, and record debt")
    if decision.get("verification_finality") not in {
        "bounded_refresh_required",
        "proof_verified_but_not_authority",
        "proof_failed_quarantine_sustained",
        "held_pending_proof",
        "conflict_held",
    }:
        errors.append("verification_decision.verification_finality invalid")


def validate_receipt(receipt: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    top_level_ok(receipt, errors)
    ref = receipt.get("source_remediation_closure_ref")
    if not isinstance(ref, dict):
        errors.append("source_remediation_closure_ref must be an object")
    else:
        resolve_source_closure(ref, errors)
    scope_ok(receipt, errors)
    evidence_ok(receipt, errors)
    controls_ok(receipt, errors)
    projection_ok(receipt, errors)
    decision_ok(receipt, errors)
    return errors


def main() -> int:
    return run_fixture_checker(
        fixture_dir=INTAKE_DIR,
        valid_glob="*.valid.json",
        invalid_glob="*.invalid.json",
        validate_receipt=validate_receipt,
        label="Governance verification-intake receipt",
    )


if __name__ == "__main__":
    sys.exit(main())
