"""rev0076 delivery evidence for redacted-summary writes.

Delivery evidence is deliberately separate from summary drain readiness.  A
missing ACK, useful refusal, NACK, or payload mismatch each has different local
meaning and must not be compressed into a single boolean.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_DELIVERY_WITNESS_DOMAIN = DOMAIN + b":summary-delivery-witness-v1:"


class SummaryDeliveryObservationKind(str, Enum):
    ACK_DELIVERED = "ack_delivered"
    USEFUL_REFUSAL = "useful_refusal"
    MISSING_ACK = "missing_ack"
    NACK = "nack"
    PAYLOAD_MISMATCH = "payload_mismatch"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTION_OK = "redaction_ok"


class SummaryDeliveryDecisionKind(str, Enum):
    ACCEPT_SUMMARY_DELIVERY_ACK = "accept_summary_delivery_ack"
    HOLD_DRAIN_PENDING = "hold_drain_pending"
    HOLD_USEFUL_REFUSAL = "hold_useful_refusal"
    HOLD_MISSING_ACK = "hold_missing_ack"
    HOLD_MISSING_REQUIRED_OBSERVATION = "hold_missing_required_observation"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_PAYLOAD_MISMATCH = "quarantine_payload_mismatch"
    QUARANTINE_NACK = "quarantine_nack"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SummaryDeliveryObservation:
    observation_kind: SummaryDeliveryObservationKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_drain_digest: bytes
    summary_send_canary_digest: bytes
    accepted_drain_marker_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
    redacted_summary_digest: bytes
    remote_ack_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(SUMMARY_DELIVERY_WITNESS_DOMAIN + b":observation:" + bencode({
            b"kind": SummaryDeliveryObservationKind(self.observation_kind).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"drain": self.summary_drain_digest,
            b"canary": self.summary_send_canary_digest,
            b"drain_marker": self.accepted_drain_marker_digest,
            b"destination": self.destination_digest,
            b"sam": self.sam_endpoint_digest,
            b"redacted_summary": self.redacted_summary_digest,
            b"ack": self.remote_ack_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryDeliveryWitnessReport:
    decision_kind: SummaryDeliveryDecisionKind
    accept: bool
    watch: bool
    summary_delivery_acked: bool
    delivery_settled: bool
    useful_refusal_seen: bool
    missing_ack_seen: bool
    contradiction_preserved: bool
    contradiction_carried: bool
    redacted: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_drain_digest: bytes
    summary_send_canary_digest: bytes
    accepted_observation_digest: bytes
    accepted_drain_marker_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
    redacted_summary_digest: bytes
    observation_values: tuple[str, ...]
    observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
        getattr(report, "retry_idempotency_key", ZERO_DIGEST),
    )


def _observation_boundary(obs: SummaryDeliveryObservation) -> tuple[Any, ...]:
    return (
        SideEffectAction(obs.action),
        obs.profile_id,
        obs.service_name,
        obs.scope_digest,
        obs.request_digest,
        obs.payload_digest,
        obs.idempotency_key,
        obs.retry_idempotency_key,
    )


def make_summary_delivery_observation(
    *,
    observation_kind: SummaryDeliveryObservationKind,
    sequence: int,
    summary_drain_report: Any,
    previous_digest: bytes = ZERO_DIGEST,
    remote_ack_digest: bytes | None = None,
    contradiction_carried: bool = True,
    raw_boundary_exposed: bool = False,
    raw_payload_exposed: bool = False,
    family_id: str = "summary-delivery-family",
    path_family_id: str = "summary-delivery-path",
    hard_negative_count: int = 0,
) -> SummaryDeliveryObservation:
    ack = remote_ack_digest or sha256(SUMMARY_DELIVERY_WITNESS_DOMAIN + b":ack:" + _digest(summary_drain_report))
    return SummaryDeliveryObservation(
        observation_kind=SummaryDeliveryObservationKind(observation_kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_drain_report, "action")),
        profile_id=getattr(summary_drain_report, "profile_id"),
        service_name=getattr(summary_drain_report, "service_name"),
        scope_digest=getattr(summary_drain_report, "scope_digest"),
        request_digest=getattr(summary_drain_report, "request_digest"),
        payload_digest=getattr(summary_drain_report, "payload_digest"),
        idempotency_key=getattr(summary_drain_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_drain_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_drain_digest=_digest(summary_drain_report),
        summary_send_canary_digest=getattr(summary_drain_report, "summary_send_canary_digest", ZERO_DIGEST),
        accepted_drain_marker_digest=getattr(summary_drain_report, "accepted_marker_digest", ZERO_DIGEST),
        destination_digest=getattr(summary_drain_report, "destination_digest", ZERO_DIGEST),
        sam_endpoint_digest=getattr(summary_drain_report, "sam_endpoint_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_drain_report, "redacted_summary_digest", ZERO_DIGEST),
        remote_ack_digest=ack,
        contradiction_carried=contradiction_carried,
        raw_boundary_exposed=raw_boundary_exposed,
        raw_payload_exposed=raw_payload_exposed,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(
    kind: SummaryDeliveryDecisionKind,
    accept: bool,
    watch: bool,
    acked: bool,
    refusal: bool,
    missing: bool,
    contradiction: bool,
    redacted: bool,
    reason: str,
    *,
    summary_drain_report: Any,
    observations: tuple[SummaryDeliveryObservation, ...],
    accepted_observation_digest: bytes = ZERO_DIGEST,
) -> SummaryDeliveryWitnessReport:
    values = tuple(sorted({obs.observation_kind.value for obs in observations}))
    digests = tuple(obs.observation_digest for obs in observations)
    families = {obs.family_id for obs in observations}
    paths = {obs.path_family_id for obs in observations}
    hard = int(getattr(summary_drain_report, "hard_negative_count", 0) or 0) + sum(obs.hard_negative_count for obs in observations)
    report_digest = sha256(SUMMARY_DELIVERY_WITNESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"acked": 1 if acked else 0,
        b"refusal": 1 if refusal else 0,
        b"missing": 1 if missing else 0,
        b"drain": _digest(summary_drain_report),
        b"accepted": accepted_observation_digest,
        b"observations": list(digests),
        b"values": list(values),
        b"families": len(families),
        b"paths": len(paths),
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryDeliveryWitnessReport(
        decision_kind=kind,
        accept=accept,
        watch=watch,
        summary_delivery_acked=acked,
        delivery_settled=acked,
        useful_refusal_seen=refusal,
        missing_ack_seen=missing,
        contradiction_preserved=contradiction,
        contradiction_carried=contradiction,
        redacted=redacted,
        reason=reason,
        action=SideEffectAction(getattr(summary_drain_report, "action")),
        profile_id=getattr(summary_drain_report, "profile_id"),
        service_name=getattr(summary_drain_report, "service_name"),
        scope_digest=getattr(summary_drain_report, "scope_digest"),
        request_digest=getattr(summary_drain_report, "request_digest"),
        payload_digest=getattr(summary_drain_report, "payload_digest"),
        idempotency_key=getattr(summary_drain_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_drain_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_drain_digest=_digest(summary_drain_report),
        summary_send_canary_digest=getattr(summary_drain_report, "summary_send_canary_digest", ZERO_DIGEST),
        accepted_observation_digest=accepted_observation_digest,
        accepted_drain_marker_digest=getattr(summary_drain_report, "accepted_marker_digest", ZERO_DIGEST),
        destination_digest=getattr(summary_drain_report, "destination_digest", ZERO_DIGEST),
        sam_endpoint_digest=getattr(summary_drain_report, "sam_endpoint_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_drain_report, "redacted_summary_digest", ZERO_DIGEST),
        observation_values=values,
        observation_digests=digests,
        family_count=len(families),
        path_family_count=len(paths),
        hard_negative_count=hard,
        report_digest=report_digest,
    )


def assess_summary_delivery_witness(
    *,
    summary_drain_report: Any,
    observations: tuple[SummaryDeliveryObservation, ...],
    previous_digest: bytes = ZERO_DIGEST,
    required_observations: tuple[SummaryDeliveryObservationKind, ...] = (
        SummaryDeliveryObservationKind.ACK_DELIVERED,
        SummaryDeliveryObservationKind.REDACTION_OK,
        SummaryDeliveryObservationKind.CONTRADICTION_MEMORY,
    ),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SummaryDeliveryWitnessReport:
    observations = tuple(observations)
    if not getattr(summary_drain_report, "summary_drain_ready", False):
        return _report(SummaryDeliveryDecisionKind.HOLD_DRAIN_PENDING, False, True, False, False, False, False, False, "summary drain pending", summary_drain_report=summary_drain_report, observations=observations)
    boundary = _boundary(summary_drain_report)
    if any(_observation_boundary(obs) != boundary for obs in observations):
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, False, False, "observation boundary drift", summary_drain_report=summary_drain_report, observations=observations)
    for obs in observations:
        if (
            obs.summary_drain_digest != _digest(summary_drain_report)
            or obs.summary_send_canary_digest != getattr(summary_drain_report, "summary_send_canary_digest", ZERO_DIGEST)
            or obs.accepted_drain_marker_digest != getattr(summary_drain_report, "accepted_marker_digest", ZERO_DIGEST)
            or obs.destination_digest != getattr(summary_drain_report, "destination_digest", ZERO_DIGEST)
            or obs.sam_endpoint_digest != getattr(summary_drain_report, "sam_endpoint_digest", ZERO_DIGEST)
            or obs.redacted_summary_digest != getattr(summary_drain_report, "redacted_summary_digest", ZERO_DIGEST)
        ):
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, False, False, "observation digest drift", summary_drain_report=summary_drain_report, observations=observations)
        if obs.raw_boundary_exposed or obs.raw_payload_exposed:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, False, False, "raw boundary or payload exposure", summary_drain_report=summary_drain_report, observations=observations)

    kinds = {obs.observation_kind for obs in observations}
    redacted = bool(getattr(summary_drain_report, "redacted", False) and SummaryDeliveryObservationKind.REDACTION_OK in kinds)
    contradiction = bool(getattr(summary_drain_report, "contradiction_preserved", False) and all(obs.contradiction_carried for obs in observations) and SummaryDeliveryObservationKind.CONTRADICTION_MEMORY in kinds)
    if not contradiction:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, False, False, redacted, "contradiction memory missing", summary_drain_report=summary_drain_report, observations=observations)
    hard = int(getattr(summary_drain_report, "hard_negative_count", 0) or 0) + sum(obs.hard_negative_count for obs in observations)
    if hard:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, False, False, True, redacted, "hard-negative pressure", summary_drain_report=summary_drain_report, observations=observations)
    if SummaryDeliveryObservationKind.PAYLOAD_MISMATCH in kinds:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_PAYLOAD_MISMATCH, False, True, False, False, False, True, redacted, "payload mismatch", summary_drain_report=summary_drain_report, observations=observations)
    if SummaryDeliveryObservationKind.NACK in kinds:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_NACK, False, True, False, False, False, True, redacted, "negative ACK", summary_drain_report=summary_drain_report, observations=observations)
    if SummaryDeliveryObservationKind.USEFUL_REFUSAL in kinds:
        return _report(SummaryDeliveryDecisionKind.HOLD_USEFUL_REFUSAL, False, True, False, True, False, True, redacted, "useful refusal observed", summary_drain_report=summary_drain_report, observations=observations)
    if SummaryDeliveryObservationKind.MISSING_ACK in kinds or SummaryDeliveryObservationKind.ACK_DELIVERED not in kinds:
        return _report(SummaryDeliveryDecisionKind.HOLD_MISSING_ACK, False, True, False, False, True, True, redacted, "missing ACK", summary_drain_report=summary_drain_report, observations=observations)
    if not set(required_observations).issubset(kinds):
        return _report(SummaryDeliveryDecisionKind.HOLD_MISSING_REQUIRED_OBSERVATION, False, True, False, False, False, True, redacted, "missing required observation", summary_drain_report=summary_drain_report, observations=observations)

    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for obs in sorted(observations, key=lambda item: item.sequence):
        digest = obs.observation_digest
        if digest in seen_digests:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, True, redacted, "replayed observation", summary_drain_report=summary_drain_report, observations=observations)
        seen_digests.add(digest)
        if obs.sequence <= 0:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, True, redacted, "non-positive sequence", summary_drain_report=summary_drain_report, observations=observations)
        if obs.sequence in seen_sequences and seen_sequences[obs.sequence] != digest:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, True, redacted, "same-sequence fork", summary_drain_report=summary_drain_report, observations=observations)
        seen_sequences[obs.sequence] = digest
        if obs.previous_digest != previous:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, True, redacted, "previous-link mismatch", summary_drain_report=summary_drain_report, observations=observations)
        previous = digest

    if len({obs.family_id for obs in observations}) < min_family_count:
        return _report(SummaryDeliveryDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, True, redacted, "low family diversity", summary_drain_report=summary_drain_report, observations=observations)
    if len({obs.path_family_id for obs in observations}) < min_path_family_count:
        return _report(SummaryDeliveryDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, True, redacted, "low path diversity", summary_drain_report=summary_drain_report, observations=observations)

    accepted = previous if observations else ZERO_DIGEST
    return _report(SummaryDeliveryDecisionKind.ACCEPT_SUMMARY_DELIVERY_ACK, True, False, True, False, False, True, redacted, "summary delivery ACK accepted", summary_drain_report=summary_drain_report, observations=observations, accepted_observation_digest=accepted)
