"""Timeline validation for Priority-0 external replay custody records.

The current causal contract does not compare wall clocks from different
operators or machines.  It validates responder-local and custodian-local order
separately; exact response/prerequisite hashes carry causality across stages.
Historical custody records remain executable under their original chronology.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from priority_zero_causal_artifact_lib import (
    CURRENT_CUSTODY_CONTRACT,
    CausalArtifactError,
    timestamp,
    validate_local_order,
)

LEGACY_THREE_STAGE_CONTRACT = "three-stage-v2"


class CustodyTimelineError(ValueError):
    pass


@dataclass(frozen=True)
class CustodyTimelineSummary:
    responder_id: str
    custodian_id: str
    run_started_at: str
    run_completed_at: str
    response_frozen_at: str
    chronology_contract: str
    custody_kit_opened_at: str | None = None
    response_observed_at: str | None = None
    custody_record_frozen_at: str | None = None
    scorer_opened_at: str | None = None
    chronology_state: str = "valid"
    distinct_custodian: bool = True
    cross_operator_time_ordering: str = "not-used"

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "responder_id": self.responder_id,
            "custodian_id": self.custodian_id,
            "run_started_at": self.run_started_at,
            "run_completed_at": self.run_completed_at,
            "response_frozen_at": self.response_frozen_at,
            "custody_timeline_state": self.chronology_state,
            "custody_chronology_contract": self.chronology_contract,
            "distinct_custodian": self.distinct_custodian,
            "cross_operator_time_ordering": self.cross_operator_time_ordering,
        }
        if self.custody_kit_opened_at is not None:
            result["custody_kit_opened_at"] = self.custody_kit_opened_at
        if self.response_observed_at is not None:
            result["response_observed_at"] = self.response_observed_at
        if self.custody_record_frozen_at is not None:
            result["custody_record_frozen_at"] = self.custody_record_frozen_at
        if self.scorer_opened_at is not None:
            result["scorer_opened_at"] = self.scorer_opened_at
        return result


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CustodyTimelineError(f"{label} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        return timestamp(value, label)[1]
    except CausalArtifactError as exc:
        raise CustodyTimelineError(str(exc)) from exc


def _parse_ordered_fields(fields: list[tuple[str, Any]]) -> tuple[list[str], list[datetime]]:
    originals: list[str] = []
    parsed: list[datetime] = []
    for label, value in fields:
        text = _non_empty_string(value, label)
        originals.append(text)
        parsed.append(_parse_timestamp(text, label))
    for index in range(1, len(parsed)):
        if parsed[index] < parsed[index - 1]:
            previous = fields[index - 1][0].split(".")[-1]
            current = fields[index][0].split(".")[-1]
            raise CustodyTimelineError(
                f"custody timeline impossible: {current} precedes {previous}"
            )
    return originals, parsed


def validate_custody_timeline(
    response: dict[str, Any],
    evidence_record: dict[str, Any],
    *,
    require_distinct_custodian: bool = False,
) -> CustodyTimelineSummary:
    stage = response.get("responder_stage")
    if not isinstance(stage, dict):
        raise CustodyTimelineError("response missing responder_stage object")
    att = evidence_record.get("custodian_attestation")
    if not isinstance(att, dict):
        raise CustodyTimelineError("custody evidence missing custodian_attestation object")

    responder_id = _non_empty_string(stage.get("responder_id"), "responder_stage.responder_id")
    custody_responder_id = _non_empty_string(att.get("responder_id"), "custodian_attestation.responder_id")
    custodian_id = _non_empty_string(att.get("custodian_id"), "custodian_attestation.custodian_id")
    if custody_responder_id != responder_id:
        raise CustodyTimelineError("custody responder_id must match response responder_id")
    if require_distinct_custodian and custodian_id == responder_id:
        raise CustodyTimelineError("custodian_id must differ from response responder_id")

    contract = evidence_record.get("custody_contract_version")
    if contract == CURRENT_CUSTODY_CONTRACT:
        try:
            responder_texts, _ = validate_local_order(
                [
                    ("responder_stage.run_started_at", stage.get("run_started_at")),
                    ("responder_stage.run_completed_at", stage.get("run_completed_at")),
                ],
                boundary="responder-local timeline",
            )
            custodian_texts, _ = validate_local_order(
                [
                    ("custodian_attestation.custody_kit_opened_at", att.get("custody_kit_opened_at")),
                    ("custodian_attestation.response_observed_at", att.get("response_observed_at")),
                    ("custodian_attestation.custody_record_frozen_at", att.get("custody_record_frozen_at")),
                ],
                boundary="custodian-local timeline",
            )
            response_frozen_at, _ = timestamp(
                att.get("response_frozen_at"),
                "custodian_attestation.response_frozen_at",
            )
        except CausalArtifactError as exc:
            raise CustodyTimelineError(str(exc)) from exc
        return CustodyTimelineSummary(
            responder_id=responder_id,
            custodian_id=custodian_id,
            run_started_at=responder_texts[0],
            run_completed_at=responder_texts[1],
            response_frozen_at=response_frozen_at,
            custody_kit_opened_at=custodian_texts[0],
            response_observed_at=custodian_texts[1],
            custody_record_frozen_at=custodian_texts[2],
            chronology_contract=CURRENT_CUSTODY_CONTRACT,
            distinct_custodian=(custodian_id != responder_id),
            cross_operator_time_ordering="exact-artifact-hash-chain-not-wall-clock",
        )

    if contract == LEGACY_THREE_STAGE_CONTRACT:
        fields = [
            ("responder_stage.run_started_at", stage.get("run_started_at")),
            ("responder_stage.run_completed_at", stage.get("run_completed_at")),
            ("custodian_attestation.response_frozen_at", att.get("response_frozen_at")),
            ("custodian_attestation.custody_kit_opened_at", att.get("custody_kit_opened_at")),
            ("custodian_attestation.custody_record_frozen_at", att.get("custody_record_frozen_at")),
        ]
        originals, _ = _parse_ordered_fields(fields)
        return CustodyTimelineSummary(
            responder_id=responder_id,
            custodian_id=custodian_id,
            run_started_at=originals[0],
            run_completed_at=originals[1],
            response_frozen_at=originals[2],
            custody_kit_opened_at=originals[3],
            custody_record_frozen_at=originals[4],
            chronology_contract=LEGACY_THREE_STAGE_CONTRACT,
            distinct_custodian=(custodian_id != responder_id),
            cross_operator_time_ordering="legacy-wall-clock-comparison",
        )

    # Historical compatibility: archived rev0371-rev0374 fixtures place the
    # scorer-open timestamp in the custody record. Current records must not.
    fields = [
        ("responder_stage.run_started_at", stage.get("run_started_at")),
        ("responder_stage.run_completed_at", stage.get("run_completed_at")),
        ("custodian_attestation.response_frozen_at", att.get("response_frozen_at")),
        ("custodian_attestation.scorer_opened_at", att.get("scorer_opened_at")),
    ]
    originals, _ = _parse_ordered_fields(fields)
    return CustodyTimelineSummary(
        responder_id=responder_id,
        custodian_id=custodian_id,
        run_started_at=originals[0],
        run_completed_at=originals[1],
        response_frozen_at=originals[2],
        scorer_opened_at=originals[3],
        chronology_contract="legacy-scorer-open-in-custody-record",
        distinct_custodian=(custodian_id != responder_id),
        cross_operator_time_ordering="legacy-wall-clock-comparison",
    )
