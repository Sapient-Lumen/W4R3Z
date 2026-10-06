"""Causal artifact-chain primitives for the current Priority-0 external run.

Cross-operator wall clocks are observations, not a trustworthy ordering
mechanism.  The current contract therefore proves stage order with exact file
hashes and validates time order only inside the process that produced a stage
artifact.  Historical contracts remain in their existing adapters.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    parse_timestamp,
)

CURRENT_CUSTODY_CONTRACT = "causal-three-stage-v3"
CURRENT_SCORING_CONTRACT = CURRENT_CUSTODY_CONTRACT
CURRENT_RESPONSE_SET_CONTRACT = "all-arms-causal-freeze-v3"
CURRENT_POLICY_VERIFICATION_CONTRACT = "postfreeze-policy-causal-verification-v3"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OBSERVATION_FIELDS = {
    "label",
    "artifact_sha256",
    "observed_at",
    "observed_at_source",
}


class CausalArtifactError(ValueError):
    """Raised when a local chronology or exact-artifact receipt is malformed."""


def sha256_text(value: Any, label: str) -> str:
    try:
        text = non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise CausalArtifactError(str(exc)) from exc
    if not SHA256_RE.fullmatch(text):
        raise CausalArtifactError(f"{label} must be a lowercase SHA-256 digest")
    return text


def timestamp(value: Any, label: str) -> tuple[str, datetime]:
    try:
        return parse_timestamp(value, label)
    except ExternalRunArtifactError as exc:
        raise CausalArtifactError(str(exc)) from exc


def validate_local_order(
    fields: list[tuple[str, Any]],
    *,
    boundary: str,
) -> tuple[list[str], list[datetime]]:
    """Require monotonic timestamps emitted by one local stage/process."""
    texts: list[str] = []
    parsed: list[datetime] = []
    for label, value in fields:
        text, instant = timestamp(value, label)
        texts.append(text)
        parsed.append(instant)
    for index in range(1, len(parsed)):
        if parsed[index] < parsed[index - 1]:
            previous = fields[index - 1][0].split(".")[-1]
            current = fields[index][0].split(".")[-1]
            raise CausalArtifactError(
                f"{boundary}: local clock moved backward; {current} precedes {previous}"
            )
    return texts, parsed


def validate_local_window(
    value: Any,
    *,
    label: str,
    opened_at: datetime,
    frozen_at: datetime,
    boundary: str,
) -> str:
    text, instant = timestamp(value, label)
    if instant < opened_at or instant > frozen_at:
        raise CausalArtifactError(
            f"{boundary}: {label.split('.')[-1]} lies outside the producing stage's local open/freeze window"
        )
    return text


def validate_observation_rows(
    rows: Any,
    *,
    required_labels: list[str],
    opened_at: datetime,
    frozen_at: datetime,
    expected_source: str,
    label: str,
) -> dict[str, dict[str, str]]:
    """Validate ordered exact-artifact receipts captured by one local stage."""
    if not isinstance(rows, list):
        raise CausalArtifactError(f"{label} must be a list")
    if len(rows) != len(required_labels):
        raise CausalArtifactError(
            f"{label} count drifted: observed={len(rows)} expected={len(required_labels)}"
        )
    result: dict[str, dict[str, str]] = {}
    observed_labels: list[str] = []
    for index, row in enumerate(rows):
        row_label = f"{label}[{index}]"
        if not isinstance(row, dict) or set(row) != OBSERVATION_FIELDS:
            raise CausalArtifactError(
                f"{row_label} fields drifted: observed={sorted(row) if isinstance(row, dict) else type(row).__name__} "
                f"expected={sorted(OBSERVATION_FIELDS)}"
            )
        try:
            artifact_label = non_placeholder_text(row.get("label"), f"{row_label}.label")
        except ExternalRunArtifactError as exc:
            raise CausalArtifactError(str(exc)) from exc
        if artifact_label in result:
            raise CausalArtifactError(f"{label} contains duplicate label: {artifact_label}")
        digest = sha256_text(row.get("artifact_sha256"), f"{row_label}.artifact_sha256")
        if row.get("observed_at_source") != expected_source:
            raise CausalArtifactError(
                f"{row_label}.observed_at_source must be {expected_source}"
            )
        observed_at = validate_local_window(
            row.get("observed_at"),
            label=f"{row_label}.observed_at",
            opened_at=opened_at,
            frozen_at=frozen_at,
            boundary=label,
        )
        result[artifact_label] = {
            "artifact_sha256": digest,
            "observed_at": observed_at,
            "observed_at_source": expected_source,
        }
        observed_labels.append(artifact_label)
    if observed_labels != required_labels:
        raise CausalArtifactError(
            f"{label} labels/order drifted: observed={observed_labels} expected={required_labels}"
        )
    return result
