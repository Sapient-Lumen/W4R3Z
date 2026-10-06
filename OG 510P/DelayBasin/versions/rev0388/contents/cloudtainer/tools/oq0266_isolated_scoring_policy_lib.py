"""Preanswer-bound scoring-policy contract for the OQ-0266 isolated pilot.

The assignment mapping may remain hidden until all responses freeze, but the
rules that determine admissibility and scoring must not be chosen after seeing
those responses.  This module defines a scorer-key-free validation shape that
can ship in the prefreeze kit.  The policy content itself remains postfreeze;
its exact SHA-256 is committed inside the responder-bound assignment
commitment.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
from datetime import datetime
from typing import Any

from oq0266_isolated_commitment_lib import (
    CommitmentContractError,
    validate_assignment_commitment,
)
from priority_zero_causal_artifact_lib import (
    CURRENT_POLICY_VERIFICATION_CONTRACT,
    CausalArtifactError,
    validate_local_order,
)
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    parse_timestamp,
)

SCORING_POLICY_CONTRACT_VERSION = "preanswer-scoring-policy-v1"
SCORING_POLICY_RECORD_TYPE = "isolated-scoring-policy"
POLICY_VERIFICATION_CONTRACT_VERSION = CURRENT_POLICY_VERIFICATION_CONTRACT
POLICY_VERIFICATION_RECORD_TYPE = "isolated-postfreeze-policy-verification"
POLICY_VERIFICATION_STATE = "postfreeze-policy-matches-preanswer-commitment"
POLICY_VERIFICATION_STARTED_AT_SOURCE = "local-process-clock-at-postfreeze-policy-verifier-start"
POLICY_LOCK_OBSERVED_AT_SOURCE = "local-process-clock-after-response-set-lock-validation"
POLICY_VERIFIED_AT_SOURCE = "local-process-clock-before-postfreeze-policy-receipt-write"

POLICY_FIELDS = {
    "project",
    "id",
    "record_type",
    "scoring_policy_contract_version",
    "batch_id",
    "revision",
    "created_at",
    "assignment_plan_sha256",
    "required_variants",
    "decision_thresholds",
    "global_requirements",
    "tool_sha256_by_surface",
    "arms",
    "non_claim",
}
POLICY_ARM_FIELDS = {"arm_code", "scorer_policy"}
GLOBAL_REQUIREMENT_FIELDS = {
    "all_responses_before_postfreeze",
    "distinct_responder_per_arm",
    "collector_distinct_from_responders",
    "custodian_distinct_from_responder",
    "scorer_distinct_from_responder",
    "custody_before_scoring",
    "metric_rationales_required",
    "packet_notes_required",
    "positive_per_packet_cost_required",
    "cost_sum_match_required",
    "strict_json_required",
    "current_tool_hashes_required",
    "cross_operator_order_carried_by_exact_artifact_receipts",
    "manual_run_manifest_hash_transcription_forbidden",
    "self_contained_source_kit_evidence_capsule_required",
    "separately_preserved_outer_digest_required",
    "bounded_safe_nested_zip_parsing_required",
    "postassembly_dynamic_or_source_artifact_replacement_rejected",
}
REQUIRED_TRUE_GLOBAL_REQUIREMENTS = frozenset(GLOBAL_REQUIREMENT_FIELDS)

# These fields bind one scorer intake to concrete generated artifacts and may be
# computed only after the responder bundle exists.  Everything else in the
# scorer intake is policy and must exactly match its preanswer commitment.
SCORER_RUNTIME_BINDING_FIELDS = {
    "id",
    "revision",
    "surface",
    "created_at",
    "responder_only_surface",
    "responder_only_sha256",
    "response_template_surface",
    "response_template_sha256",
    "responder_bundle_surface",
    "responder_bundle_sha256",
    "evidence_record_template_surface",
    "evidence_record_template_sha256",
    "score_sheet_template_surface",
    "score_sheet_template_sha256",
    "scorer_kit_surface",
    "custody_kit_surface",
    "scoring_policy_surface",
    "scoring_policy_sha256",
}

VERIFICATION_RECEIPT_FIELDS = {
    "project",
    "id",
    "record_type",
    "policy_verification_contract_version",
    "batch_id",
    "assignment_commitment_sha256",
    "assignment_plan_sha256",
    "scoring_policy_sha256",
    "dispatch_manifest_sha256",
    "response_set_lock_sha256",
    "verifier_id",
    "response_set_locked_at",
    "verification_started_at",
    "verification_started_at_source",
    "response_set_lock_observed_at",
    "response_set_lock_observed_at_source",
    "verified_at",
    "verified_at_source",
    "postfreeze_material_opened_only_after_response_set_lock",
    "scorer_intake_sha256_by_arm",
    "responder_packet_projection_sha256_by_arm",
    "tool_sha256_by_surface",
    "verification_state",
    "non_claim",
}


class ScoringPolicyContractError(ValueError):
    """Raised when postfreeze scoring material drifts from preanswer policy."""


def _exact_fields(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScoringPolicyContractError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise ScoringPolicyContractError(
            f"{label} fields drifted: observed={sorted(observed)} expected={sorted(expected)}"
        )
    return value


def _text(value: Any, label: str) -> str:
    try:
        return non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise ScoringPolicyContractError(str(exc)) from exc


def _timestamp(value: Any, label: str) -> tuple[str, datetime]:
    try:
        return parse_timestamp(value, label)
    except ExternalRunArtifactError as exc:
        raise ScoringPolicyContractError(str(exc)) from exc


def _sha256(value: Any, label: str) -> str:
    text = _text(value, label)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ScoringPolicyContractError(f"{label} must be a lowercase SHA-256 hex digest")
    return text


def file_sha256(path: pathlib.Path) -> str:
    if not path.exists() or not path.is_file():
        raise ScoringPolicyContractError(f"missing committed policy input: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ScoringPolicyContractError(f"policy value is not canonical strict JSON: {exc}") from exc


def scorer_policy_projection(scorer: dict[str, Any]) -> dict[str, Any]:
    """Return all non-runtime scorer fields as one exact policy projection."""
    if not isinstance(scorer, dict):
        raise ScoringPolicyContractError("scorer intake must be an object")
    projection = {
        key: value for key, value in scorer.items() if key not in SCORER_RUNTIME_BINDING_FIELDS
    }
    if not projection:
        raise ScoringPolicyContractError("scorer policy projection must not be empty")
    return projection


def _validate_thresholds(value: Any) -> dict[str, Any]:
    thresholds = _exact_fields(
        value,
        {
            "compact_min_score",
            "sham_max_score",
            "baseline_max_score",
            "trace_override_margin",
            "support_if_trace_minus_compact_at_most",
        },
        "scoring policy decision_thresholds",
    )
    for key, raw in thresholds.items():
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ScoringPolicyContractError(f"scoring policy decision_thresholds.{key} must be numeric")
        if not math.isfinite(float(raw)):
            raise ScoringPolicyContractError(f"scoring policy decision_thresholds.{key} must be finite")
    return thresholds


def validate_scoring_policy(
    policy: dict[str, Any],
    assignment_plan: dict[str, Any],
    *,
    assignment_plan_sha256: str,
    root: pathlib.Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Validate policy, assignment agreement, and committed tool bytes."""
    _exact_fields(policy, POLICY_FIELDS, "scoring policy")
    if policy.get("project") != "DelayBasin":
        raise ScoringPolicyContractError("scoring policy project must be DelayBasin")
    if policy.get("record_type") != SCORING_POLICY_RECORD_TYPE:
        raise ScoringPolicyContractError(
            f"scoring policy record_type must be {SCORING_POLICY_RECORD_TYPE}"
        )
    if policy.get("scoring_policy_contract_version") != SCORING_POLICY_CONTRACT_VERSION:
        raise ScoringPolicyContractError(
            f"scoring policy contract must be {SCORING_POLICY_CONTRACT_VERSION}"
        )
    _text(policy.get("id"), "scoring policy id")
    batch_id = _text(policy.get("batch_id"), "scoring policy batch_id")
    _text(policy.get("revision"), "scoring policy revision")
    _timestamp(policy.get("created_at"), "scoring policy created_at")
    _text(policy.get("non_claim"), "scoring policy non_claim")
    if assignment_plan.get("project") != "DelayBasin":
        raise ScoringPolicyContractError("assignment plan project must be DelayBasin")
    if assignment_plan.get("batch_id") != batch_id:
        raise ScoringPolicyContractError("scoring policy batch_id disagrees with assignment plan")
    if _sha256(
        policy.get("assignment_plan_sha256"),
        "scoring policy assignment_plan_sha256",
    ) != assignment_plan_sha256:
        raise ScoringPolicyContractError(
            "scoring policy assignment_plan_sha256 disagrees with supplied assignment plan bytes"
        )

    variants = policy.get("required_variants")
    if variants != ["baseline", "compact", "sham", "trace"]:
        raise ScoringPolicyContractError(
            "scoring policy required_variants must be exactly baseline, compact, sham, trace"
        )
    plan_thresholds = assignment_plan.get("decision_thresholds")
    policy_thresholds = _validate_thresholds(policy.get("decision_thresholds"))
    if canonical_json(policy_thresholds) != canonical_json(plan_thresholds):
        raise ScoringPolicyContractError(
            "scoring policy decision thresholds disagree with the committed assignment plan"
        )

    requirements = _exact_fields(
        policy.get("global_requirements"),
        GLOBAL_REQUIREMENT_FIELDS,
        "scoring policy global_requirements",
    )
    for key in REQUIRED_TRUE_GLOBAL_REQUIREMENTS:
        if requirements.get(key) is not True:
            raise ScoringPolicyContractError(
                f"scoring policy global_requirements.{key} must be true"
            )

    plan_rows = assignment_plan.get("arms")
    if not isinstance(plan_rows, list) or len(plan_rows) != 4:
        raise ScoringPolicyContractError("assignment plan must contain exactly four arm rows")
    plan_by_arm: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(plan_rows):
        if not isinstance(row, dict):
            raise ScoringPolicyContractError(f"assignment plan arms[{index}] must be an object")
        arm = _text(row.get("arm_code"), f"assignment plan arms[{index}].arm_code")
        if arm in plan_by_arm:
            raise ScoringPolicyContractError(f"assignment plan duplicates arm {arm}")
        plan_by_arm[arm] = row

    rows = policy.get("arms")
    if not isinstance(rows, list) or len(rows) != 4:
        raise ScoringPolicyContractError("scoring policy must contain exactly four arm rows")
    policy_by_arm: dict[str, dict[str, Any]] = {}
    for index, row_value in enumerate(rows):
        row = _exact_fields(row_value, POLICY_ARM_FIELDS, f"scoring policy arms[{index}]")
        arm = _text(row.get("arm_code"), f"scoring policy arms[{index}].arm_code")
        if arm in policy_by_arm:
            raise ScoringPolicyContractError(f"scoring policy duplicates arm {arm}")
        scorer_policy = row.get("scorer_policy")
        if not isinstance(scorer_policy, dict):
            raise ScoringPolicyContractError(f"scoring policy {arm}.scorer_policy must be an object")
        if scorer_policy.get("project") != "DelayBasin":
            raise ScoringPolicyContractError(f"scoring policy {arm} scorer project must be DelayBasin")
        if scorer_policy.get("batch_id") != batch_id or scorer_policy.get("arm_code") != arm:
            raise ScoringPolicyContractError(
                f"scoring policy {arm} scorer identity disagrees with policy batch"
            )
        for key in [
            "requires_distinct_scorer_from_responder",
            "requires_distinct_custodian",
            "requires_custody_timeline_order",
            "requires_score_sheet_chronology",
            "requires_metric_rationales",
            "requires_packet_score_notes",
            "requires_per_packet_operator_cost",
            "requires_operator_cost_sum_match",
            "requires_bound_custody_record_file",
            "requires_bound_score_sheet_file",
            "requires_separate_score_sheet",
            "requires_tool_finalized_response",
        ]:
            if scorer_policy.get(key) is not True:
                raise ScoringPolicyContractError(
                    f"scoring policy {arm}.{key} must be true"
                )
        answer_key = scorer_policy.get("answer_key")
        if not isinstance(answer_key, dict) or set(answer_key) != {arm}:
            raise ScoringPolicyContractError(
                f"scoring policy {arm} must contain exactly one opaque answer-key row"
            )
        key_row = answer_key[arm]
        plan_row = plan_by_arm.get(arm)
        if not isinstance(key_row, dict) or plan_row is None:
            raise ScoringPolicyContractError(f"scoring policy {arm} mapping is malformed")
        for plan_field, key_field in [
            ("source_packet_label", "source_packet_label"),
            ("analysis_variant", "analysis_variant"),
            ("expected_posture", "expected_posture"),
            ("reference_expected_score", "expected_score"),
        ]:
            if plan_row.get(plan_field) != key_row.get(key_field):
                raise ScoringPolicyContractError(
                    f"scoring policy {arm} {key_field} disagrees with assignment plan"
                )
        policy_by_arm[arm] = scorer_policy
    if set(policy_by_arm) != set(plan_by_arm):
        raise ScoringPolicyContractError(
            "scoring policy arm set disagrees with assignment plan"
        )

    tool_claims = policy.get("tool_sha256_by_surface")
    if not isinstance(tool_claims, dict) or not tool_claims:
        raise ScoringPolicyContractError(
            "scoring policy tool_sha256_by_surface must be a non-empty object"
        )
    observed_tools: dict[str, str] = {}
    for surface, digest_value in tool_claims.items():
        surface_text = _text(surface, "scoring policy tool surface")
        expected_digest = _sha256(
            digest_value,
            f"scoring policy tool_sha256_by_surface[{surface_text}]",
        )
        path = root / surface_text
        observed = file_sha256(path)
        if observed != expected_digest:
            raise ScoringPolicyContractError(
                f"committed postfreeze tool hash drifted: {surface_text}"
            )
        observed_tools[surface_text] = observed
    return policy_by_arm, observed_tools


def validate_scorer_against_policy(
    scorer: dict[str, Any],
    *,
    expected_policy: dict[str, Any],
    arm: str,
    scoring_policy_surface: str,
    scoring_policy_sha256: str,
) -> None:
    """Reject added, removed, or changed scorer policy fields."""
    runtime_fields = SCORER_RUNTIME_BINDING_FIELDS
    expected_fields = set(expected_policy) | runtime_fields
    observed_fields = set(scorer)
    if observed_fields != expected_fields:
        raise ScoringPolicyContractError(
            f"arm {arm} scorer fields drifted from committed policy/runtime split: "
            f"observed={sorted(observed_fields)} expected={sorted(expected_fields)}"
        )
    projection = scorer_policy_projection(scorer)
    if canonical_json(projection) != canonical_json(expected_policy):
        raise ScoringPolicyContractError(
            f"arm {arm} scorer policy projection drifted from preanswer commitment"
        )
    if scorer.get("scoring_policy_surface") != scoring_policy_surface:
        raise ScoringPolicyContractError(
            f"arm {arm} scorer scoring_policy_surface drifted"
        )
    if scorer.get("scoring_policy_sha256") != scoring_policy_sha256:
        raise ScoringPolicyContractError(
            f"arm {arm} scorer scoring_policy_sha256 drifted"
        )


def validate_policy_commitment(
    commitment: dict[str, Any],
    *,
    assignment_plan_sha256: str,
    scoring_policy_sha256: str,
) -> dict[str, str]:
    """Validate plan, policy, and opaque responder-stimulus commitments."""
    try:
        summary = validate_assignment_commitment(
            commitment,
            assignment_plan_sha256=assignment_plan_sha256,
            scoring_policy_sha256=scoring_policy_sha256,
            scoring_policy_contract_version=SCORING_POLICY_CONTRACT_VERSION,
        )
    except CommitmentContractError as exc:
        raise ScoringPolicyContractError(str(exc)) from exc
    return summary.responder_packet_projection_sha256_by_arm


def validate_policy_verification_receipt(
    receipt: dict[str, Any],
    *,
    batch_id: str,
    assignment_commitment_sha256: str,
    assignment_plan_sha256: str,
    scoring_policy_sha256: str,
    dispatch_manifest_sha256: str,
    response_set_lock_sha256: str,
    response_set_locked_at: str,
    scorer_intake_sha256_by_arm: dict[str, str],
    responder_packet_projection_sha256_by_arm: dict[str, str],
    tool_sha256_by_surface: dict[str, str],
) -> tuple[str, datetime]:
    _exact_fields(receipt, VERIFICATION_RECEIPT_FIELDS, "postfreeze policy verification receipt")
    if receipt.get("project") != "DelayBasin":
        raise ScoringPolicyContractError(
            "postfreeze policy verification receipt project must be DelayBasin"
        )
    if receipt.get("record_type") != POLICY_VERIFICATION_RECORD_TYPE:
        raise ScoringPolicyContractError(
            f"postfreeze policy verification record_type must be {POLICY_VERIFICATION_RECORD_TYPE}"
        )
    if receipt.get("policy_verification_contract_version") != POLICY_VERIFICATION_CONTRACT_VERSION:
        raise ScoringPolicyContractError(
            f"postfreeze policy verification contract must be {POLICY_VERIFICATION_CONTRACT_VERSION}"
        )
    if receipt.get("verification_state") != POLICY_VERIFICATION_STATE:
        raise ScoringPolicyContractError(
            f"postfreeze policy verification state must be {POLICY_VERIFICATION_STATE}"
        )
    _text(receipt.get("id"), "postfreeze policy verification id")
    verifier_id = _text(receipt.get("verifier_id"), "postfreeze policy verifier_id")
    _text(receipt.get("non_claim"), "postfreeze policy verification non_claim")
    if receipt.get("batch_id") != batch_id:
        raise ScoringPolicyContractError(
            "postfreeze policy verification batch_id disagrees with assignment plan"
        )
    expected_hashes = {
        "assignment_commitment_sha256": assignment_commitment_sha256,
        "assignment_plan_sha256": assignment_plan_sha256,
        "scoring_policy_sha256": scoring_policy_sha256,
        "dispatch_manifest_sha256": dispatch_manifest_sha256,
        "response_set_lock_sha256": response_set_lock_sha256,
    }
    for field, expected in expected_hashes.items():
        if _sha256(receipt.get(field), f"postfreeze policy verification {field}") != expected:
            raise ScoringPolicyContractError(
                f"postfreeze policy verification {field} disagrees with current artifact bytes"
            )
    if receipt.get("postfreeze_material_opened_only_after_response_set_lock") is not True:
        raise ScoringPolicyContractError(
            "postfreeze policy verification must attest postfreeze opening only after the response-set lock"
        )
    expected_sources = {
        "verification_started_at_source": POLICY_VERIFICATION_STARTED_AT_SOURCE,
        "response_set_lock_observed_at_source": POLICY_LOCK_OBSERVED_AT_SOURCE,
        "verified_at_source": POLICY_VERIFIED_AT_SOURCE,
    }
    for field, expected in expected_sources.items():
        if receipt.get(field) != expected:
            raise ScoringPolicyContractError(
                f"postfreeze policy verification {field} must be {expected}"
            )
    locked_text, _ = _timestamp(
        receipt.get("response_set_locked_at"),
        "postfreeze policy verification response_set_locked_at",
    )
    if locked_text != response_set_locked_at:
        raise ScoringPolicyContractError(
            "postfreeze policy verification response_set_locked_at disagrees with response-set lock"
        )
    try:
        local_texts, local_times = validate_local_order(
            [
                ("postfreeze verification verification_started_at", receipt.get("verification_started_at")),
                ("postfreeze verification response_set_lock_observed_at", receipt.get("response_set_lock_observed_at")),
                ("postfreeze verification verified_at", receipt.get("verified_at")),
            ],
            boundary="postfreeze-verifier-local timeline",
        )
    except CausalArtifactError as exc:
        raise ScoringPolicyContractError(str(exc)) from exc
    verified_text = local_texts[2]
    verified_at = local_times[2]
    if receipt.get("scorer_intake_sha256_by_arm") != scorer_intake_sha256_by_arm:
        raise ScoringPolicyContractError(
            "postfreeze policy verification scorer-intake hashes disagree with current files"
        )
    if (
        receipt.get("responder_packet_projection_sha256_by_arm")
        != responder_packet_projection_sha256_by_arm
    ):
        raise ScoringPolicyContractError(
            "postfreeze policy verification responder-packet projection hashes disagree with the preanswer commitment"
        )
    if receipt.get("tool_sha256_by_surface") != tool_sha256_by_surface:
        raise ScoringPolicyContractError(
            "postfreeze policy verification tool hashes disagree with current files"
        )
    return verifier_id, verified_at
