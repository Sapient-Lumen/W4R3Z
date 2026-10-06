"""Prefreeze-safe response-set contract for the OQ-0266 isolated pilot.

The isolated pilot is only clean when every one-arm response is frozen before
any assignment mapping, custody template, scorer intake, or score sheet opens.
Per-arm response-before-custody checks are insufficient: one arm can otherwise
enter postfreeze processing while later responders are still working.

This module contains no assignment mapping or scorer key.  It is safe to ship
in the prefreeze dispatch kit and is reused by the final batch scorer so both
sides interpret the response-set lock identically.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from priority_zero_causal_artifact_lib import (
    CURRENT_RESPONSE_SET_CONTRACT,
    CausalArtifactError,
    validate_local_order,
    validate_local_window,
)
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    parse_timestamp,
)

RESPONSE_SET_CONTRACT_VERSION = CURRENT_RESPONSE_SET_CONTRACT
RESPONSE_SET_RECORD_TYPE = "isolated-response-set-lock"
RESPONSE_SET_STATE = "all-arm-exact-responses-observed-and-locked-before-postfreeze-open"
EXPECTED_ARM_COUNT = 4
LOCK_CLOCK_SOURCE = "local-process-clock-at-response-set-lock"
RESPONSE_OBSERVED_CLOCK_SOURCE = "local-process-clock-after-finalized-response-validation"

DISPATCH_FIELDS = {
    "project",
    "id",
    "batch_id",
    "revision",
    "created_at",
    "response_set_contract_version",
    "assignment_commitment_surface",
    "assignment_commitment_sha256",
    "arm_count",
    "minimum_distinct_responders",
    "arms",
    "prefreeze_visibility_boundary",
    "postfreeze_visibility_boundary",
    "non_claim",
}
DISPATCH_ARM_FIELDS = {
    "arm_code",
    "responder_bundle_surface",
    "responder_bundle_sha256",
    "responder_bundle_members",
    "responder_packet_surface",
    "responder_packet_sha256",
    "responder_packet_projection_sha256",
    "response_template_surface",
    "response_template_sha256",
}
LOCK_FIELDS = {
    "project",
    "id",
    "record_type",
    "response_set_contract_version",
    "batch_id",
    "dispatch_manifest_sha256",
    "assignment_commitment_sha256",
    "response_count",
    "distinct_responder_count",
    "response_set_state",
    "responses",
    "collector_attestation",
    "non_claim",
}
LOCK_RESPONSE_FIELDS = {
    "arm_code",
    "response_file_sha256",
    "responder_id",
    "response_finalized_at",
    "response_observed_at",
    "response_observed_at_source",
    "responder_bundle_sha256",
    "responder_packet_sha256",
    "responder_packet_projection_sha256",
}
COLLECTOR_FIELDS = {
    "collector_id",
    "collection_started_at",
    "response_set_locked_at",
    "response_set_locked_at_source",
    "postfreeze_kit_not_opened_before_response_set_lock",
    "assignment_mapping_not_opened_before_response_set_lock",
    "all_responses_received_as_tool_finalized_artifacts",
    "collector_is_distinct_from_all_responders",
    "exposure_notes",
}
REQUIRED_COLLECTOR_ATTESTATIONS = {
    "postfreeze_kit_not_opened_before_response_set_lock",
    "assignment_mapping_not_opened_before_response_set_lock",
    "all_responses_received_as_tool_finalized_artifacts",
    "collector_is_distinct_from_all_responders",
}
# These fields or paths would reveal assignment/scoring information in a
# prefreeze dispatch artifact.  Hash commitments and opaque arm codes are safe.
FORBIDDEN_PREFREEZE_KEYS = {
    "analysis_variant",
    "source_packet_label",
    "expected_posture",
    "reference_expected_score",
    "expected_score",
    "true_variant",
    "answer_key",
    "decision_thresholds",
    "scorer_intake_surface",
    "scorer_intake_sha256",
    "custody_template_surface",
    "custody_template_sha256",
    "score_sheet_template_surface",
    "score_sheet_template_sha256",
}
FORBIDDEN_PREFREEZE_PATH_FRAGMENTS = (
    "assignment-plan.json",
    "scorer-intake.json",
    "custody-template.json",
    "score-sheet-template.json",
    "postfreeze-batch-kit.zip",
)


class ResponseSetContractError(ValueError):
    """Raised when dispatch or response-set evidence violates the live contract."""


@dataclass(frozen=True)
class ResponseSetLockSummary:
    batch_id: str
    collector_id: str
    collection_started_at: str
    response_set_locked_at: str
    response_set_locked: datetime
    response_count: int
    distinct_responder_count: int
    responses_by_arm: dict[str, dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "collector_id": self.collector_id,
            "collection_started_at": self.collection_started_at,
            "response_set_locked_at": self.response_set_locked_at,
            "response_count": self.response_count,
            "distinct_responder_count": self.distinct_responder_count,
            "response_set_state": RESPONSE_SET_STATE,
            "cross_operator_time_ordering": "exact-response-hash-chain-not-wall-clock",
        }


def _artifact_error(exc: ExternalRunArtifactError) -> ResponseSetContractError:
    return ResponseSetContractError(str(exc))


def _exact_fields(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ResponseSetContractError(f"{label} must be an object")
    observed = set(value)
    if observed != expected:
        raise ResponseSetContractError(
            f"{label} fields drifted: observed={sorted(observed)} expected={sorted(expected)}"
        )
    return value


def _hex_sha256(value: Any, label: str) -> str:
    try:
        text = non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise _artifact_error(exc) from exc
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ResponseSetContractError(f"{label} must be a lowercase SHA-256 hex digest")
    return text


def _reject_sensitive_prefreeze_content(value: Any, label: str) -> None:
    if isinstance(value, dict):
        leaked = sorted(set(value) & FORBIDDEN_PREFREEZE_KEYS)
        if leaked:
            raise ResponseSetContractError(f"{label} leaked postfreeze keys: {leaked}")
        for key, child in value.items():
            _reject_sensitive_prefreeze_content(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_prefreeze_content(child, f"{label}[{index}]")
    elif isinstance(value, str):
        for fragment in FORBIDDEN_PREFREEZE_PATH_FRAGMENTS:
            if fragment in value:
                raise ResponseSetContractError(
                    f"{label} leaked postfreeze path fragment: {fragment}"
                )


def validate_dispatch_manifest(
    manifest: dict[str, Any],
    *,
    assignment_commitment_sha256: str | None = None,
    responder_packet_projection_sha256_by_arm: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Validate the exact prefreeze-safe dispatch manifest and return arms by code."""
    _exact_fields(manifest, DISPATCH_FIELDS, "dispatch manifest")
    _reject_sensitive_prefreeze_content(manifest, "dispatch manifest")
    if manifest.get("project") != "DelayBasin":
        raise ResponseSetContractError("dispatch manifest project must be DelayBasin")
    try:
        non_placeholder_text(manifest.get("id"), "dispatch manifest id")
        batch_id = non_placeholder_text(manifest.get("batch_id"), "dispatch manifest batch_id")
        non_placeholder_text(manifest.get("revision"), "dispatch manifest revision")
        parse_timestamp(manifest.get("created_at"), "dispatch manifest created_at")
        non_placeholder_text(
            manifest.get("assignment_commitment_surface"),
            "dispatch manifest assignment_commitment_surface",
        )
        non_placeholder_text(
            manifest.get("prefreeze_visibility_boundary"),
            "dispatch manifest prefreeze_visibility_boundary",
        )
        non_placeholder_text(
            manifest.get("postfreeze_visibility_boundary"),
            "dispatch manifest postfreeze_visibility_boundary",
        )
        non_placeholder_text(manifest.get("non_claim"), "dispatch manifest non_claim")
    except ExternalRunArtifactError as exc:
        raise _artifact_error(exc) from exc
    if manifest.get("response_set_contract_version") != RESPONSE_SET_CONTRACT_VERSION:
        raise ResponseSetContractError(
            f"dispatch response_set_contract_version must be {RESPONSE_SET_CONTRACT_VERSION}"
        )
    if manifest.get("arm_count") != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(f"dispatch arm_count must be {EXPECTED_ARM_COUNT}")
    if manifest.get("minimum_distinct_responders") != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(
            f"dispatch minimum_distinct_responders must be {EXPECTED_ARM_COUNT}"
        )
    commitment_sha = _hex_sha256(
        manifest.get("assignment_commitment_sha256"),
        "dispatch manifest assignment_commitment_sha256",
    )
    if assignment_commitment_sha256 is not None and commitment_sha != assignment_commitment_sha256:
        raise ResponseSetContractError(
            "dispatch manifest assignment commitment hash disagrees with supplied commitment file"
        )

    rows = manifest.get("arms")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(
            f"dispatch manifest must contain exactly {EXPECTED_ARM_COUNT} arm rows"
        )
    by_arm: dict[str, dict[str, Any]] = {}
    bundle_surfaces: set[str] = set()
    for index, row_value in enumerate(rows):
        row = _exact_fields(row_value, DISPATCH_ARM_FIELDS, f"dispatch arms[{index}]")
        try:
            arm = non_placeholder_text(row.get("arm_code"), f"dispatch arms[{index}].arm_code")
            bundle_surface = non_placeholder_text(
                row.get("responder_bundle_surface"),
                f"dispatch {arm}.responder_bundle_surface",
            )
            packet_surface = non_placeholder_text(
                row.get("responder_packet_surface"),
                f"dispatch {arm}.responder_packet_surface",
            )
            template_surface = non_placeholder_text(
                row.get("response_template_surface"),
                f"dispatch {arm}.response_template_surface",
            )
        except ExternalRunArtifactError as exc:
            raise _artifact_error(exc) from exc
        if arm in by_arm:
            raise ResponseSetContractError(f"dispatch manifest duplicates arm {arm}")
        if bundle_surface in bundle_surfaces:
            raise ResponseSetContractError(
                f"dispatch manifest reuses responder bundle surface {bundle_surface}"
            )
        members = row.get("responder_bundle_members")
        if not isinstance(members, list) or not members or not all(
            isinstance(item, str) and item for item in members
        ):
            raise ResponseSetContractError(
                f"dispatch {arm}.responder_bundle_members must be a non-empty string list"
            )
        if len(members) != len(set(members)):
            raise ResponseSetContractError(f"dispatch {arm} responder bundle members must be unique")
        if packet_surface not in members or template_surface not in members:
            raise ResponseSetContractError(
                f"dispatch {arm} bundle members must contain its packet and response template"
            )
        for field in [
            "responder_bundle_sha256",
            "responder_packet_sha256",
            "responder_packet_projection_sha256",
            "response_template_sha256",
        ]:
            _hex_sha256(row.get(field), f"dispatch {arm}.{field}")
        by_arm[arm] = row
        bundle_surfaces.add(bundle_surface)
    if len(by_arm) != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError("dispatch manifest arm codes must be unique")
    if responder_packet_projection_sha256_by_arm is not None:
        if set(responder_packet_projection_sha256_by_arm) != set(by_arm):
            raise ResponseSetContractError(
                "dispatch responder-packet projection arm set disagrees with the preanswer commitment"
            )
        for arm, row in by_arm.items():
            if (
                row.get("responder_packet_projection_sha256")
                != responder_packet_projection_sha256_by_arm[arm]
            ):
                raise ResponseSetContractError(
                    f"dispatch {arm} responder-packet projection disagrees with the preanswer commitment"
                )
    # Keep the parsed value live so accidental removal is caught by callers.
    if not batch_id:
        raise ResponseSetContractError("dispatch manifest batch_id must not be empty")
    return by_arm


def validate_response_set_lock(
    lock: dict[str, Any],
    dispatch_manifest: dict[str, Any],
    *,
    dispatch_manifest_sha256: str,
    assignment_commitment_sha256: str,
    responder_packet_projection_sha256_by_arm: dict[str, str],
    expected_responses_by_arm: dict[str, dict[str, Any]] | None = None,
) -> ResponseSetLockSummary:
    """Validate the all-response barrier and optionally bind current response bytes."""
    _exact_fields(lock, LOCK_FIELDS, "response-set lock")
    if lock.get("project") != "DelayBasin":
        raise ResponseSetContractError("response-set lock project must be DelayBasin")
    if lock.get("record_type") != RESPONSE_SET_RECORD_TYPE:
        raise ResponseSetContractError(
            f"response-set lock record_type must be {RESPONSE_SET_RECORD_TYPE}"
        )
    if lock.get("response_set_contract_version") != RESPONSE_SET_CONTRACT_VERSION:
        raise ResponseSetContractError(
            f"response-set lock contract must be {RESPONSE_SET_CONTRACT_VERSION}"
        )
    if lock.get("response_set_state") != RESPONSE_SET_STATE:
        raise ResponseSetContractError(
            f"response-set lock state must be {RESPONSE_SET_STATE}"
        )
    try:
        non_placeholder_text(lock.get("id"), "response-set lock id")
        batch_id = non_placeholder_text(lock.get("batch_id"), "response-set lock batch_id")
        non_placeholder_text(lock.get("non_claim"), "response-set lock non_claim")
    except ExternalRunArtifactError as exc:
        raise _artifact_error(exc) from exc
    if batch_id != dispatch_manifest.get("batch_id"):
        raise ResponseSetContractError("response-set lock batch_id disagrees with dispatch manifest")
    if _hex_sha256(
        lock.get("dispatch_manifest_sha256"),
        "response-set lock dispatch_manifest_sha256",
    ) != dispatch_manifest_sha256:
        raise ResponseSetContractError(
            "response-set lock dispatch_manifest_sha256 does not match supplied dispatch bytes"
        )
    if _hex_sha256(
        lock.get("assignment_commitment_sha256"),
        "response-set lock assignment_commitment_sha256",
    ) != assignment_commitment_sha256:
        raise ResponseSetContractError(
            "response-set lock assignment commitment does not match supplied commitment bytes"
        )
    if lock.get("response_count") != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(f"response-set lock response_count must be {EXPECTED_ARM_COUNT}")
    if lock.get("distinct_responder_count") != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(
            f"response-set lock distinct_responder_count must be {EXPECTED_ARM_COUNT}"
        )

    dispatch_by_arm = validate_dispatch_manifest(
        dispatch_manifest,
        assignment_commitment_sha256=assignment_commitment_sha256,
        responder_packet_projection_sha256_by_arm=responder_packet_projection_sha256_by_arm,
    )
    rows = lock.get("responses")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(
            f"response-set lock must contain exactly {EXPECTED_ARM_COUNT} response rows"
        )
    responses_by_arm: dict[str, dict[str, Any]] = {}
    responder_ids: list[str] = []
    parsed_response_observations: list[tuple[str, str, datetime]] = []
    for index, row_value in enumerate(rows):
        row = _exact_fields(row_value, LOCK_RESPONSE_FIELDS, f"response-set responses[{index}]")
        try:
            arm = non_placeholder_text(row.get("arm_code"), f"response-set responses[{index}].arm_code")
            responder_id = non_placeholder_text(
                row.get("responder_id"),
                f"response-set {arm}.responder_id",
            )
            finalized_text, _ = parse_timestamp(
                row.get("response_finalized_at"),
                f"response-set {arm}.response_finalized_at",
            )
            observed_text, observed_at = parse_timestamp(
                row.get("response_observed_at"),
                f"response-set {arm}.response_observed_at",
            )
        except ExternalRunArtifactError as exc:
            raise _artifact_error(exc) from exc
        if arm in responses_by_arm:
            raise ResponseSetContractError(f"response-set lock duplicates arm {arm}")
        if arm not in dispatch_by_arm:
            raise ResponseSetContractError(f"response-set lock names unknown arm {arm}")
        for field in [
            "response_file_sha256",
            "responder_bundle_sha256",
            "responder_packet_sha256",
            "responder_packet_projection_sha256",
        ]:
            _hex_sha256(row.get(field), f"response-set {arm}.{field}")
        dispatch_row = dispatch_by_arm[arm]
        if row.get("responder_bundle_sha256") != dispatch_row.get("responder_bundle_sha256"):
            raise ResponseSetContractError(
                f"response-set {arm} responder bundle hash disagrees with dispatch manifest"
            )
        if row.get("responder_packet_sha256") != dispatch_row.get("responder_packet_sha256"):
            raise ResponseSetContractError(
                f"response-set {arm} responder packet hash disagrees with dispatch manifest"
            )
        if (
            row.get("responder_packet_projection_sha256")
            != responder_packet_projection_sha256_by_arm.get(arm)
        ):
            raise ResponseSetContractError(
                f"response-set {arm} responder-packet projection disagrees with the preanswer commitment"
            )
        if row.get("response_observed_at_source") != RESPONSE_OBSERVED_CLOCK_SOURCE:
            raise ResponseSetContractError(
                f"response-set {arm}.response_observed_at_source must be {RESPONSE_OBSERVED_CLOCK_SOURCE}"
            )
        normalized = dict(row)
        normalized["response_finalized_at"] = finalized_text
        normalized["response_observed_at"] = observed_text
        responses_by_arm[arm] = normalized
        responder_ids.append(responder_id)
        parsed_response_observations.append((arm, observed_text, observed_at))
    if set(responses_by_arm) != set(dispatch_by_arm):
        raise ResponseSetContractError(
            "response-set lock arm set disagrees with dispatch manifest"
        )
    if len(responder_ids) != len(set(responder_ids)):
        duplicates = sorted({value for value in responder_ids if responder_ids.count(value) > 1})
        raise ResponseSetContractError(
            "response-set lock requires one distinct responder per arm; duplicates: "
            + ", ".join(duplicates)
        )

    collector = _exact_fields(
        lock.get("collector_attestation"),
        COLLECTOR_FIELDS,
        "response-set collector_attestation",
    )
    try:
        collector_id = non_placeholder_text(
            collector.get("collector_id"),
            "response-set collector_attestation.collector_id",
        )
        collection_started_text, collection_started = parse_timestamp(
            collector.get("collection_started_at"),
            "response-set collector_attestation.collection_started_at",
        )
        locked_text, locked_at = parse_timestamp(
            collector.get("response_set_locked_at"),
            "response-set collector_attestation.response_set_locked_at",
        )
        non_placeholder_text(
            collector.get("exposure_notes"),
            "response-set collector_attestation.exposure_notes",
        )
    except ExternalRunArtifactError as exc:
        raise _artifact_error(exc) from exc
    if collector.get("response_set_locked_at_source") != LOCK_CLOCK_SOURCE:
        raise ResponseSetContractError(
            f"response-set lock timestamp source must be {LOCK_CLOCK_SOURCE}"
        )
    for field in REQUIRED_COLLECTOR_ATTESTATIONS:
        if collector.get(field) is not True:
            raise ResponseSetContractError(
                f"response-set collector_attestation.{field} must be true"
            )
    try:
        validate_local_order(
            [
                ("collector_attestation.collection_started_at", collection_started_text),
                ("collector_attestation.response_set_locked_at", locked_text),
            ],
            boundary="collector-local response-set timeline",
        )
        for arm, observed_text, _ in parsed_response_observations:
            validate_local_window(
                observed_text,
                label=f"response-set {arm}.response_observed_at",
                opened_at=collection_started,
                frozen_at=locked_at,
                boundary="collector-local response observation",
            )
    except CausalArtifactError as exc:
        raise ResponseSetContractError(str(exc)) from exc
    if collector_id in set(responder_ids):
        raise ResponseSetContractError(
            "response-set collector_id must differ from every responder_id"
        )

    if expected_responses_by_arm is not None:
        if set(expected_responses_by_arm) != set(responses_by_arm):
            raise ResponseSetContractError(
                "current response file arm set disagrees with response-set lock"
            )
        for arm, expected in expected_responses_by_arm.items():
            observed = responses_by_arm[arm]
            for field in LOCK_RESPONSE_FIELDS - {"arm_code"}:
                if observed.get(field) != expected.get(field):
                    raise ResponseSetContractError(
                        f"response-set lock {arm}.{field} does not match the current validated response"
                    )

    return ResponseSetLockSummary(
        batch_id=batch_id,
        collector_id=collector_id,
        collection_started_at=collection_started_text,
        response_set_locked_at=locked_text,
        response_set_locked=locked_at,
        response_count=len(responses_by_arm),
        distinct_responder_count=len(set(responder_ids)),
        responses_by_arm=responses_by_arm,
    )
