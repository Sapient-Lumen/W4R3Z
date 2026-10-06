"""Shared current custody contract for the Priority-0 external replay.

The live ``causal-three-stage-v3`` contract binds exact artifacts across
operators and validates time order only within the process that emitted each
stage record.  It deliberately does not treat independent wall clocks as a
trusted chronology source.  Historical formats remain in final-scorer adapters.
"""
from __future__ import annotations

from typing import Any

from priority_zero_causal_artifact_lib import (
    CURRENT_CUSTODY_CONTRACT,
    CausalArtifactError,
    timestamp,
    validate_observation_rows,
)
from priority_zero_custody_timeline_lib import (
    CustodyTimelineError,
    validate_custody_timeline,
)
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
)
from priority_zero_external_replay_response_lib import (
    CURRENT_RESPONSE_PREPARATION_CONTRACT,
)

CURRENT_EVIDENCE_STATE = "completed-response-and-causal-custody-record-frozen-before-scorer-kit"
EXPECTED_TIMESTAMP_SOURCES = {
    "response_frozen_at_source": "response.response_artifact.finalized_at",
    "custody_kit_opened_at_source": "local-process-clock-at-custody-helper-start",
    "response_observed_at_source": "local-process-clock-after-finalized-response-validation",
    "custody_record_frozen_at_source": "local-process-clock-before-custody-write",
}
PREREQUISITE_OBSERVED_CLOCK_SOURCE = "local-process-clock-after-prerequisite-read"
REQUIRED_CURRENT_ATTESTATIONS = (
    "responder_was_given_only_responder_bundle_before_response",
    "full_archive_not_given_before_response",
    "conversation_not_shown_before_response",
    "answer_key_not_shown_before_response",
    "response_hash_recorded_before_custody_record_frozen",
    "custodian_is_distinct_from_responder",
    "custody_helper_observed_exact_response_before_record_freeze",
    "required_prerequisites_observed_before_custody_record_frozen",
    "scorer_kit_not_opened_before_custody_record_frozen",
    "score_sheet_template_not_opened_before_custody_record_frozen",
    "handoff_manifest_not_opened_before_custody_record_frozen",
)
LEGACY_TOP_LEVEL_FIELDS = ("scorer_intake_surface", "scorer_intake_sha256")
LEGACY_ATTESTATION_FIELDS = (
    "scorer_opened_at",
    "scorer_intake_opened_only_after_response_frozen",
    "response_hash_recorded_before_scoring",
    "score_sheet_template_opened_only_after_response_frozen",
    "handoff_manifest_opened_only_after_response_frozen",
    "custody_kit_opened_only_after_response_frozen",
)
DYNAMIC_TOP_LEVEL_FIELDS = {
    "id",
    "evidence_state",
    "response_file_sha256",
    "response_finalized_at",
    "prerequisite_artifacts",
    "custodian_attestation",
}


class CurrentCustodyContractError(ValueError):
    """Raised when a live causal custody record is not admissible."""


def _raise_from_artifact(exc: ExternalRunArtifactError) -> None:
    raise CurrentCustodyContractError(str(exc)) from exc


def _material_entries(value: Any) -> list[str]:
    if isinstance(value, str):
        entries = [value.strip()] if value.strip() else []
    elif isinstance(value, list):
        entries = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise CurrentCustodyContractError(
                    "custodian_attestation.pre_response_materials_given entries must be non-empty strings"
                )
            entries.append(item.strip())
    else:
        raise CurrentCustodyContractError(
            "custodian_attestation.pre_response_materials_given must be a string or list of strings"
        )
    if not entries:
        raise CurrentCustodyContractError(
            "custodian_attestation.pre_response_materials_given must not be empty"
        )
    return entries


def _required_prerequisite_labels(template: dict[str, Any]) -> list[str]:
    value = template.get("required_prerequisite_labels")
    if not isinstance(value, list):
        raise CurrentCustodyContractError(
            "current custody template required_prerequisite_labels must be a list"
        )
    labels: list[str] = []
    for index, item in enumerate(value):
        try:
            text = non_placeholder_text(item, f"required_prerequisite_labels[{index}]")
        except ExternalRunArtifactError as exc:
            _raise_from_artifact(exc)
        if text in labels:
            raise CurrentCustodyContractError(
                f"current custody template contains duplicate prerequisite label: {text}"
            )
        labels.append(text)
    return labels


def validate_current_custody_record(
    evidence_record: dict[str, Any],
    custody_template: dict[str, Any],
    *,
    response: dict[str, Any],
    response_summary: dict[str, Any],
    response_file_sha256: str,
) -> dict[str, Any]:
    """Validate the complete live custody artifact and return a stable summary."""
    try:
        if not isinstance(evidence_record, dict):
            raise CurrentCustodyContractError("strict external scoring requires a separate custody evidence record")
        if not isinstance(custody_template, dict):
            raise CurrentCustodyContractError("current custody template could not be loaded")
        if custody_template.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT:
            raise CurrentCustodyContractError(
                f"current custody template is not {CURRENT_CUSTODY_CONTRACT}"
            )
        if custody_template.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise CurrentCustodyContractError(
                "current custody template does not require responder-finalize-v1"
            )
        if evidence_record.get("project") != "DelayBasin":
            raise CurrentCustodyContractError("custody evidence record project must be DelayBasin")
        if evidence_record.get("record_type") != "custody-evidence-record":
            raise CurrentCustodyContractError(
                "custody evidence record_type must be custody-evidence-record"
            )
        if evidence_record.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT:
            raise CurrentCustodyContractError(
                f"custody evidence contract mismatch: expected {CURRENT_CUSTODY_CONTRACT}"
            )
        if evidence_record.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise CurrentCustodyContractError(
                "custody evidence response preparation contract mismatch: expected responder-finalize-v1"
            )
        for legacy_key in LEGACY_TOP_LEVEL_FIELDS:
            if legacy_key in evidence_record:
                raise CurrentCustodyContractError(
                    f"current custody evidence must not contain scorer-stage field: {legacy_key}"
                )
        if set(evidence_record) != set(custody_template):
            raise CurrentCustodyContractError(
                "current custody evidence top-level fields drifted from template: "
                f"observed={sorted(evidence_record)} expected={sorted(custody_template)}"
            )
        for key, expected in custody_template.items():
            if key not in DYNAMIC_TOP_LEVEL_FIELDS and evidence_record.get(key) != expected:
                raise CurrentCustodyContractError(
                    f"current custody evidence protected template field drifted: {key}"
                )

        non_placeholder_text(evidence_record.get("id"), "custody evidence id")
        if evidence_record.get("evidence_state") != CURRENT_EVIDENCE_STATE:
            raise CurrentCustodyContractError(
                f"custody evidence state must be {CURRENT_EVIDENCE_STATE}"
            )
        if evidence_record.get("response_file_sha256") != response_file_sha256:
            raise CurrentCustodyContractError(
                "custody evidence response_file_sha256 does not match the response bytes validated by this run"
            )
        for field, label in [
            ("responder_bundle_sha256", "custody evidence responder bundle hash drifted"),
            ("responder_only_sha256", "custody evidence responder packet hash drifted"),
            ("response_template_sha256", "custody evidence response template hash drifted"),
        ]:
            if evidence_record.get(field) != custody_template.get(field):
                raise CurrentCustodyContractError(label)

        response_finalized_at = non_placeholder_text(
            evidence_record.get("response_finalized_at"),
            "custody evidence response_finalized_at",
        )
        if response_finalized_at != response_summary.get("response_finalized_at"):
            raise CurrentCustodyContractError(
                "custody response_finalized_at does not match response.response_artifact.finalized_at"
            )

        att = evidence_record.get("custodian_attestation")
        template_att = custody_template.get("custodian_attestation")
        if not isinstance(att, dict):
            raise CurrentCustodyContractError(
                "custody evidence record missing custodian_attestation object"
            )
        if not isinstance(template_att, dict) or set(att) != set(template_att):
            raise CurrentCustodyContractError(
                "current custody evidence attestation fields drifted from template"
            )
        for legacy_key in LEGACY_ATTESTATION_FIELDS:
            if legacy_key in att:
                raise CurrentCustodyContractError(
                    f"current custody evidence must not contain legacy wall-clock/scorer attestation: {legacy_key}"
                )

        for key in [
            "custodian_id",
            "responder_id",
            "response_frozen_at",
            "custody_kit_opened_at",
            "response_observed_at",
            "custody_record_frozen_at",
            "pre_response_exposure_notes",
        ]:
            non_placeholder_text(att.get(key), f"custodian_attestation.{key}")
        for key, expected in EXPECTED_TIMESTAMP_SOURCES.items():
            if att.get(key) != expected:
                raise CurrentCustodyContractError(
                    f"custodian_attestation.{key} must be {expected}"
                )
        for key in REQUIRED_CURRENT_ATTESTATIONS:
            if att.get(key) is not True:
                raise CurrentCustodyContractError(
                    f"custodian_attestation.{key} must be true for clean external evidence"
                )

        responder_id = non_placeholder_text(
            att.get("responder_id"), "custodian_attestation.responder_id"
        )
        custodian_id = non_placeholder_text(
            att.get("custodian_id"), "custodian_attestation.custodian_id"
        )
        if responder_id != response_summary.get("responder_id"):
            raise CurrentCustodyContractError(
                "custody responder_id must match response responder_id"
            )
        if custodian_id == responder_id:
            raise CurrentCustodyContractError(
                "custodian_id must differ from response responder_id"
            )
        if att.get("response_frozen_at") != response_summary.get("response_finalized_at"):
            raise CurrentCustodyContractError(
                "custody response_frozen_at does not equal the responder-reported finalized time"
            )

        expected_material = custody_template.get("responder_bundle_surface")
        expected_entries = [non_placeholder_text(expected_material, "custody template responder_bundle_surface")]
        observed_entries = _material_entries(att.get("pre_response_materials_given"))
        if sorted(observed_entries) != sorted(expected_entries):
            raise CurrentCustodyContractError(
                "custody evidence pre-response material must exactly match allowed responder-only bundle list"
            )

        try:
            timeline = validate_custody_timeline(
                response,
                evidence_record,
                require_distinct_custodian=True,
            )
            opened_at = timestamp(
                att.get("custody_kit_opened_at"),
                "custodian_attestation.custody_kit_opened_at",
            )[1]
            frozen_at = timestamp(
                att.get("custody_record_frozen_at"),
                "custodian_attestation.custody_record_frozen_at",
            )[1]
            prerequisite_map = validate_observation_rows(
                evidence_record.get("prerequisite_artifacts"),
                required_labels=_required_prerequisite_labels(custody_template),
                opened_at=opened_at,
                frozen_at=frozen_at,
                expected_source=PREREQUISITE_OBSERVED_CLOCK_SOURCE,
                label="custody prerequisite_artifacts",
            )
        except (CustodyTimelineError, CausalArtifactError) as exc:
            raise CurrentCustodyContractError(str(exc)) from exc
    except ExternalRunArtifactError as exc:
        _raise_from_artifact(exc)

    summary = timeline.as_dict()
    summary.update(
        {
            "custody_evidence_record_id": evidence_record.get("id"),
            "custody_evidence_state": evidence_record.get("evidence_state"),
            "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
            "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
            "response_file_sha256": response_file_sha256,
            "response_finalized_at": response_finalized_at,
            "pre_response_materials_given": observed_entries,
            "prerequisite_artifacts": prerequisite_map,
            "causal_ordering_basis": "exact-response-and-prerequisite-hashes-plus-producer-local-time",
        }
    )
    return summary
