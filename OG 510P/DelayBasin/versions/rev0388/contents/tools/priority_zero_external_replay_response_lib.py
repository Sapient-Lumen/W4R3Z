"""Shared current-response contract for the Priority-0 external replay.

The same validator is used before responder finalization, before custody is
spent, and again by the final scorer.  It contains no scorer key or expected
packet outcome and is therefore safe inside the responder bundle.
"""
from __future__ import annotations

from typing import Any

from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    parse_timestamp,
    positive_finite_number,
)

CURRENT_RESPONSE_PREPARATION_CONTRACT = "responder-finalize-v1"
FINAL_RESPONSE_STATE = "completed-clean-response-candidate"
TIMESTAMP_SOURCE = "local-process-clock-at-bundled-helper"
FINALIZER_TOOL = "tools/prepare_priority_zero_external_replay_response.py"
REQUIRED_ATTESTATIONS = (
    "no_scorer_key_before_response",
    "no_full_archive_before_response",
    "no_conversation_context_before_response",
)


class ResponseContractError(ValueError):
    """Raised when the current response artifact violates its shared contract."""


def _raise_from_artifact(exc: ExternalRunArtifactError) -> None:
    raise ResponseContractError(str(exc)) from exc


def _template_labels(template: dict[str, Any]) -> list[str]:
    stage = template.get("responder_stage")
    rows = stage.get("packet_answers") if isinstance(stage, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ResponseContractError("response template must contain packet answer rows")
    labels: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ResponseContractError(f"response template packet_answers[{index}] must be an object")
        label = row.get("label")
        if not isinstance(label, str) or not label:
            raise ResponseContractError(f"response template packet_answers[{index}] missing label")
        labels.append(label)
    if len(labels) != len(set(labels)):
        raise ResponseContractError("response template packet labels must be unique")
    return labels


def _required_answer_fields(template: dict[str, Any]) -> list[str]:
    fields = template.get("required_answer_fields")
    if not isinstance(fields, list) or not fields or not all(isinstance(field, str) and field for field in fields):
        raise ResponseContractError("response template required_answer_fields must be a non-empty string list")
    return fields


def validate_draft_binding(
    response: dict[str, Any],
    template: dict[str, Any],
    *,
    expected_bundle_sha256: str,
    expected_packet_sha256: str,
) -> dict[str, Any]:
    """Validate immutable identity/binding fields and completed answer content."""
    try:
        if response.get("project") != "DelayBasin":
            raise ResponseContractError("response project must be DelayBasin")
        if set(response) != set(template):
            raise ResponseContractError(
                "response top-level fields drifted from bundled template: "
                f"observed={sorted(response)} expected={sorted(template)}"
            )
        for key, expected in template.items():
            if key not in {"response_state", "responder_stage", "response_artifact"} and response.get(key) != expected:
                raise ResponseContractError(f"response protected template field drifted: {key}")
        if response.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise ResponseContractError(
                f"response_preparation_contract_version must be {CURRENT_RESPONSE_PREPARATION_CONTRACT}"
            )
        if response.get("responder_packet_surface") != template.get("responder_packet_surface"):
            raise ResponseContractError("response responder_packet_surface drifted from bundled template")
        if response.get("responder_bundle_surface") != template.get("responder_bundle_surface"):
            raise ResponseContractError("response responder_bundle_surface drifted from bundled template")

        stage = response.get("responder_stage")
        template_stage = template.get("responder_stage")
        if not isinstance(stage, dict):
            raise ResponseContractError("response missing responder_stage object")
        if not isinstance(template_stage, dict):
            raise ResponseContractError("response template missing responder_stage object")
        if set(stage) != set(template_stage):
            raise ResponseContractError(
                "responder_stage fields drifted from bundled template: "
                f"observed={sorted(stage)} expected={sorted(template_stage)}"
            )
        dynamic_stage_fields = {
            "responder_id",
            "run_started_at",
            "run_completed_at",
            "saw_responder_bundle_sha256",
            "saw_responder_packet_sha256",
            "no_scorer_key_before_response",
            "no_full_archive_before_response",
            "no_conversation_context_before_response",
            "accidental_exposure_notes",
            "operator_cost_minutes",
            "packet_answers",
        }
        for key, expected in template_stage.items():
            if key not in dynamic_stage_fields and stage.get(key) != expected:
                raise ResponseContractError(f"responder_stage protected template field drifted: {key}")
        responder_id = non_placeholder_text(stage.get("responder_id"), "responder_stage.responder_id")
        run_started_text, run_started = parse_timestamp(
            stage.get("run_started_at"), "responder_stage.run_started_at"
        )
        artifact = response.get("response_artifact")
        template_artifact = template.get("response_artifact")
        if not isinstance(artifact, dict):
            raise ResponseContractError("response missing response_artifact object")
        if not isinstance(template_artifact, dict) or set(artifact) != set(template_artifact):
            raise ResponseContractError("response_artifact fields drifted from bundled template")
        draft_created_text, draft_created = parse_timestamp(
            artifact.get("draft_created_at"), "response_artifact.draft_created_at"
        )
        if draft_created != run_started:
            raise ResponseContractError(
                "response_artifact.draft_created_at must equal responder_stage.run_started_at"
            )
        if artifact.get("timestamp_source") != TIMESTAMP_SOURCE:
            raise ResponseContractError("response_artifact timestamp_source drifted")
        if artifact.get("finalizer_tool") != FINALIZER_TOOL:
            raise ResponseContractError("response_artifact finalizer_tool drifted")
        if artifact.get("finalization_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise ResponseContractError("response_artifact finalization contract drifted")
        if stage.get("saw_responder_bundle_sha256") != expected_bundle_sha256:
            raise ResponseContractError("response observed responder bundle hash does not match the bundle finalized now")
        if stage.get("saw_responder_packet_sha256") != expected_packet_sha256:
            raise ResponseContractError("response observed responder packet hash does not match the bundled packet")

        if response.get("scorer_stage") not in (None, {}):
            raise ResponseContractError("response must not contain a scorer_stage")
        if "manual_metric_scores" in response or "manual_metric_scores" in stage:
            raise ResponseContractError("response must not contain manual_metric_scores")

        expected_labels = _template_labels(template)
        required_fields = _required_answer_fields(template)
        rows = stage.get("packet_answers")
        if not isinstance(rows, list):
            raise ResponseContractError("responder_stage.packet_answers must be a list")
        observed_labels = [row.get("label") if isinstance(row, dict) else None for row in rows]
        if observed_labels != expected_labels:
            raise ResponseContractError(
                f"response packet labels/order drifted: {observed_labels} != {expected_labels}"
            )

        packet_total = 0.0
        template_rows = template_stage.get("packet_answers")
        if not isinstance(template_rows, list):
            raise ResponseContractError("response template packet_answers must be a list")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ResponseContractError(f"packet_answers[{index}] must be an object")
            template_row = template_rows[index]
            if not isinstance(template_row, dict) or set(row) != set(template_row):
                raise ResponseContractError(
                    f"packet_answers[{index}] fields drifted from bundled template"
                )
            label = str(row.get("label"))
            packet_total += positive_finite_number(
                row.get("operator_cost_minutes"),
                f"packet_answers[{label}].operator_cost_minutes",
            )
            for field in required_fields:
                non_placeholder_text(row.get(field), f"packet_answers[{label}].{field}")
        total = positive_finite_number(
            stage.get("operator_cost_minutes"), "responder_stage.operator_cost_minutes"
        )
        if abs(total - packet_total) > 0.05:
            raise ResponseContractError(
                "responder_stage.operator_cost_minutes must equal the sum of packet operator costs within 0.05 minutes"
            )
    except ExternalRunArtifactError as exc:
        _raise_from_artifact(exc)

    return {
        "responder_id": responder_id,
        "run_started_at": run_started_text,
        "run_started": run_started,
        "draft_created_at": draft_created_text,
        "operator_cost_minutes": total,
        "packet_labels": expected_labels,
    }


def validate_finalized_response(
    response: dict[str, Any],
    template: dict[str, Any],
    *,
    expected_bundle_sha256: str,
    expected_packet_sha256: str,
) -> dict[str, Any]:
    """Validate the complete tool-finalized response before custody or scoring."""
    summary = validate_draft_binding(
        response,
        template,
        expected_bundle_sha256=expected_bundle_sha256,
        expected_packet_sha256=expected_packet_sha256,
    )
    try:
        if response.get("response_state") != FINAL_RESPONSE_STATE:
            raise ResponseContractError(f"response_state must be {FINAL_RESPONSE_STATE}")
        stage = response["responder_stage"]
        run_completed_text, run_completed = parse_timestamp(
            stage.get("run_completed_at"), "responder_stage.run_completed_at"
        )
        if run_completed < summary["run_started"]:
            raise ResponseContractError("responder_stage.run_completed_at precedes run_started_at")
        for key in REQUIRED_ATTESTATIONS:
            if stage.get(key) is not True:
                raise ResponseContractError(f"responder_stage.{key} must be true in a clean finalized response")
        exposure_notes = non_placeholder_text(
            stage.get("accidental_exposure_notes"), "responder_stage.accidental_exposure_notes"
        )

        artifact = response.get("response_artifact")
        if not isinstance(artifact, dict):
            raise ResponseContractError("response missing response_artifact object")
        if artifact.get("finalization_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise ResponseContractError("response_artifact finalization contract drifted")
        finalized_text, finalized_at = parse_timestamp(
            artifact.get("finalized_at"), "response_artifact.finalized_at"
        )
        if finalized_at != run_completed:
            raise ResponseContractError("response_artifact.finalized_at must equal responder_stage.run_completed_at")
        if artifact.get("timestamp_source") != TIMESTAMP_SOURCE:
            raise ResponseContractError("response_artifact timestamp_source drifted")
        if artifact.get("finalizer_tool") != FINALIZER_TOOL:
            raise ResponseContractError("response_artifact finalizer_tool drifted")
        if artifact.get("immutable_after_finalize") is not True:
            raise ResponseContractError("response_artifact.immutable_after_finalize must be true")
    except ExternalRunArtifactError as exc:
        _raise_from_artifact(exc)

    summary.update(
        {
            "run_completed_at": run_completed_text,
            "response_finalized_at": finalized_text,
            "response_finalized": finalized_at,
            "accidental_exposure_notes": exposure_notes,
            "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
        }
    )
    return summary
