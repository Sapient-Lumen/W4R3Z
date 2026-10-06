"""Cycle-free preanswer commitment contract for the OQ-0266 isolated pilot.

The responder packet must name the exact assignment-commitment file that was
visible before answering, but the commitment must also fix the packet's visible
stimulus.  Hashing the complete packet would create a self-reference because
the packet embeds the commitment hash.  This module therefore commits a
canonical projection that excludes only ``assignment_commitment_sha256``.
Every other responder-visible field, cue, instruction, path, and boundary
remains inside the digest.

The module contains no assignment mapping or scorer key and is safe to ship in
the prefreeze dispatch kit.  The collector, postfreeze verifier, and final
aggregator all reuse this exact interpretation.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    parse_timestamp,
)

ASSIGNMENT_COMMITMENT_CONTRACT_VERSION = "assignment-plan-policy-stimulus-v2"
ASSIGNMENT_COMMITMENT_RECORD_TYPE = "isolated-assignment-policy-stimulus-commitment"
RESPONDER_PACKET_PROJECTION_SCHEME = (
    "canonical-strict-json-of-complete-responder-packet-excluding-only-assignment_commitment_sha256-v1"
)
EXPECTED_ARM_COUNT = 4

COMMITMENT_FIELDS = {
    "project",
    "id",
    "record_type",
    "commitment_contract_version",
    "batch_id",
    "revision",
    "created_at",
    "commitment_scheme",
    "assignment_plan_sha256",
    "scoring_policy_contract_version",
    "scoring_policy_sha256",
    "responder_packet_projection_scheme",
    "responder_packet_projection_sha256_by_arm",
    "opaque_arm_codes",
    "mapping_visibility",
    "non_claim",
}


class CommitmentContractError(ValueError):
    """Raised when the preanswer plan/policy/stimulus commitment drifts."""


@dataclass(frozen=True)
class AssignmentCommitmentSummary:
    batch_id: str
    arm_codes: tuple[str, ...]
    responder_packet_projection_sha256_by_arm: dict[str, str]


def _text(value: Any, label: str) -> str:
    try:
        return non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise CommitmentContractError(str(exc)) from exc


def _sha256(value: Any, label: str) -> str:
    text = _text(value, label)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise CommitmentContractError(f"{label} must be a lowercase SHA-256 hex digest")
    return text


def _exact_fields(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CommitmentContractError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise CommitmentContractError(
            f"{label} fields drifted: observed={sorted(observed)} expected={sorted(expected)}"
        )
    return value


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CommitmentContractError(
            f"responder-packet commitment projection is not canonical strict JSON: {exc}"
        ) from exc
    return text.encode("utf-8")


def responder_packet_projection(packet: dict[str, Any]) -> dict[str, Any]:
    """Return the exact responder-visible packet minus its self-referential hash."""
    if not isinstance(packet, dict):
        raise CommitmentContractError("responder packet must be an object")
    if "assignment_commitment_sha256" not in packet:
        raise CommitmentContractError(
            "responder packet is missing assignment_commitment_sha256"
        )
    projection = {
        key: value
        for key, value in packet.items()
        if key != "assignment_commitment_sha256"
    }
    if not projection:
        raise CommitmentContractError("responder packet projection must not be empty")
    return projection


def responder_packet_projection_sha256(packet: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(responder_packet_projection(packet))).hexdigest()


def validate_assignment_commitment(
    commitment: dict[str, Any],
    *,
    assignment_plan_sha256: str | None = None,
    scoring_policy_sha256: str | None = None,
    scoring_policy_contract_version: str | None = None,
    expected_arm_codes: set[str] | None = None,
) -> AssignmentCommitmentSummary:
    """Validate the exact commitment and return its opaque stimulus digests."""
    _exact_fields(commitment, COMMITMENT_FIELDS, "assignment commitment")
    if commitment.get("project") != "DelayBasin":
        raise CommitmentContractError("assignment commitment project must be DelayBasin")
    if commitment.get("record_type") != ASSIGNMENT_COMMITMENT_RECORD_TYPE:
        raise CommitmentContractError(
            f"assignment commitment record_type must be {ASSIGNMENT_COMMITMENT_RECORD_TYPE}"
        )
    if commitment.get("commitment_contract_version") != ASSIGNMENT_COMMITMENT_CONTRACT_VERSION:
        raise CommitmentContractError(
            "assignment commitment contract must be "
            f"{ASSIGNMENT_COMMITMENT_CONTRACT_VERSION}"
        )
    _text(commitment.get("id"), "assignment commitment id")
    batch_id = _text(commitment.get("batch_id"), "assignment commitment batch_id")
    _text(commitment.get("revision"), "assignment commitment revision")
    try:
        parse_timestamp(commitment.get("created_at"), "assignment commitment created_at")
    except ExternalRunArtifactError as exc:
        raise CommitmentContractError(str(exc)) from exc
    _text(commitment.get("commitment_scheme"), "assignment commitment scheme")
    _text(commitment.get("mapping_visibility"), "assignment commitment mapping_visibility")
    _text(commitment.get("non_claim"), "assignment commitment non_claim")

    observed_plan_sha = _sha256(
        commitment.get("assignment_plan_sha256"),
        "assignment commitment assignment_plan_sha256",
    )
    observed_policy_sha = _sha256(
        commitment.get("scoring_policy_sha256"),
        "assignment commitment scoring_policy_sha256",
    )
    if assignment_plan_sha256 is not None and observed_plan_sha != assignment_plan_sha256:
        raise CommitmentContractError(
            "assignment commitment does not bind the supplied assignment plan bytes"
        )
    if scoring_policy_sha256 is not None and observed_policy_sha != scoring_policy_sha256:
        raise CommitmentContractError(
            "assignment commitment does not bind the supplied scoring policy bytes"
        )
    observed_policy_contract = _text(
        commitment.get("scoring_policy_contract_version"),
        "assignment commitment scoring_policy_contract_version",
    )
    if (
        scoring_policy_contract_version is not None
        and observed_policy_contract != scoring_policy_contract_version
    ):
        raise CommitmentContractError(
            "assignment commitment scoring-policy contract version drifted"
        )
    if commitment.get("responder_packet_projection_scheme") != RESPONDER_PACKET_PROJECTION_SCHEME:
        raise CommitmentContractError(
            "assignment commitment responder-packet projection scheme drifted"
        )

    arm_values = commitment.get("opaque_arm_codes")
    if not isinstance(arm_values, list) or len(arm_values) != EXPECTED_ARM_COUNT:
        raise CommitmentContractError(
            f"assignment commitment must name exactly {EXPECTED_ARM_COUNT} opaque arm codes"
        )
    if not all(isinstance(value, str) and value for value in arm_values):
        raise CommitmentContractError(
            "assignment commitment opaque arm codes must be non-empty strings"
        )
    if arm_values != sorted(arm_values) or len(set(arm_values)) != EXPECTED_ARM_COUNT:
        raise CommitmentContractError(
            "assignment commitment opaque arm codes must be sorted and unique"
        )
    arm_codes = set(arm_values)
    if expected_arm_codes is not None and arm_codes != expected_arm_codes:
        raise CommitmentContractError(
            "assignment commitment opaque arm set disagrees with expected arms"
        )

    projection_values = commitment.get("responder_packet_projection_sha256_by_arm")
    if not isinstance(projection_values, dict) or set(projection_values) != arm_codes:
        raise CommitmentContractError(
            "assignment commitment responder-packet projection map must name exactly its opaque arms"
        )
    projections = {
        arm: _sha256(
            projection_values[arm],
            f"assignment commitment responder_packet_projection_sha256_by_arm[{arm}]",
        )
        for arm in sorted(arm_codes)
    }
    return AssignmentCommitmentSummary(
        batch_id=batch_id,
        arm_codes=tuple(sorted(arm_codes)),
        responder_packet_projection_sha256_by_arm=projections,
    )
