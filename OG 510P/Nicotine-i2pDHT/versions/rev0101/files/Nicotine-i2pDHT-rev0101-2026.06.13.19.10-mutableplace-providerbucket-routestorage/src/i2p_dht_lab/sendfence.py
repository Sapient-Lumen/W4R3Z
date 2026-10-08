"""Send fence after live-send gate and delivery witness.

The fence is a tiny local monotonic memory surface.  It prevents a no-network
live-send permission from being reused as if it were a durable delivery result,
and it keeps pending delivery/watch states from being pruned or retried as if
nothing happened.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SEND_FENCE_DOMAIN = DOMAIN + b":send-fence-v1:"


class SendFenceDecisionKind(str, Enum):
    ACCEPT_DELIVERED_FENCE = "accept_delivered_fence"
    HOLD_PENDING_DELIVERY = "hold_pending_delivery"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SendFenceMarker:
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    live_send_gate_digest: bytes
    delivery_witness_digest: bytes
    family_id: str
    path_family_id: str

    @property
    def marker_digest(self) -> bytes:
        return sha256(SEND_FENCE_DOMAIN + b":marker:" + bencode({
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"gate": self.live_send_gate_digest,
            b"delivery": self.delivery_witness_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
        }))


@dataclass(frozen=True)
class SendFenceReport:
    decision_kind: SendFenceDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    live_send_gate_digest: bytes
    delivery_witness_digest: bytes
    accepted_marker_digest: bytes
    marker_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_send_fence_marker(*, live_send_gate_report: Any, delivery_witness_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a") -> SendFenceMarker:
    return SendFenceMarker(
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(live_send_gate_report, "action")),
        profile_id=getattr(live_send_gate_report, "profile_id"),
        service_name=getattr(live_send_gate_report, "service_name"),
        scope_digest=getattr(live_send_gate_report, "scope_digest"),
        request_digest=getattr(live_send_gate_report, "request_digest"),
        payload_digest=getattr(live_send_gate_report, "payload_digest"),
        idempotency_key=getattr(live_send_gate_report, "idempotency_key"),
        live_send_gate_digest=getattr(live_send_gate_report, "report_digest"),
        delivery_witness_digest=getattr(delivery_witness_report, "report_digest"),
        family_id=family_id,
        path_family_id=path_family_id,
    )


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _report(kind: SendFenceDecisionKind, accept: bool, watch: bool, reason: str, *, live_send_gate_report: Any, delivery_witness_report: Any | None, markers: tuple[SendFenceMarker, ...]) -> SendFenceReport:
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers if marker.family_id}
    path_families = {marker.path_family_id for marker in markers if marker.path_family_id}
    hard = int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0) + int(getattr(delivery_witness_report, "hard_negative_count", 0) or 0) if delivery_witness_report is not None else int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0)
    digest = sha256(SEND_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"gate": getattr(live_send_gate_report, "report_digest"),
        b"delivery": getattr(delivery_witness_report, "report_digest", ZERO_DIGEST),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(path_families),
        b"hard": hard,
    }))
    return SendFenceReport(kind, accept, watch, reason, SideEffectAction(getattr(live_send_gate_report, "action")), getattr(live_send_gate_report, "profile_id"), getattr(live_send_gate_report, "service_name"), getattr(live_send_gate_report, "scope_digest"), getattr(live_send_gate_report, "request_digest"), getattr(live_send_gate_report, "payload_digest"), getattr(live_send_gate_report, "idempotency_key"), getattr(live_send_gate_report, "report_digest"), getattr(delivery_witness_report, "report_digest", ZERO_DIGEST), marker_digests[-1] if accept and marker_digests else ZERO_DIGEST, marker_digests, len(families), len(path_families), hard, digest)


def assess_send_fence(*, live_send_gate_report: Any, delivery_witness_report: Any | None, markers: tuple[SendFenceMarker, ...], last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: tuple[bytes, ...] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> SendFenceReport:
    if not bool(getattr(live_send_gate_report, "accept", False)) or bool(getattr(live_send_gate_report, "quarantined", False)):
        return _report(SendFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "live-send gate not accepted", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if delivery_witness_report is None or not bool(getattr(delivery_witness_report, "accept", False)):
        return _report(SendFenceDecisionKind.HOLD_PENDING_DELIVERY, False, True, "delivery witness pending", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if bool(getattr(live_send_gate_report, "watch", False)) or bool(getattr(delivery_witness_report, "watch", False)):
        return _report(SendFenceDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if bool(getattr(delivery_witness_report, "quarantined", False)):
        return _report(SendFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "delivery witness quarantined", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if _boundary(live_send_gate_report) != _boundary(delivery_witness_report):
        return _report(SendFenceDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "delivery boundary drift", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0) + int(getattr(delivery_witness_report, "hard_negative_count", 0) or 0):
        return _report(SendFenceDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negative pressure", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if not markers:
        return _report(SendFenceDecisionKind.HOLD_PENDING_DELIVERY, False, True, "no fence markers yet", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    marker_digests = [marker.marker_digest for marker in markers]
    if any(digest in set(seen_marker_digests) for digest in marker_digests) or len(set(marker_digests)) != len(marker_digests):
        return _report(SendFenceDecisionKind.QUARANTINE_REPLAY, False, False, "send fence marker replay", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if any(marker.sequence < last_sequence for marker in markers):
        return _report(SendFenceDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "sequence rollback", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    by_seq: dict[int, set[bytes]] = {}
    for marker in markers:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(digests) > 1 for digests in by_seq.values()):
        return _report(SendFenceDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence fence fork", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    ordered = sorted(markers, key=lambda marker: marker.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(SendFenceDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "previous digest mismatch", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    expected_boundary = _boundary(live_send_gate_report)
    expected_gate = getattr(live_send_gate_report, "report_digest")
    expected_delivery = getattr(delivery_witness_report, "report_digest")
    for marker in markers:
        marker_boundary = (marker.action, marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)
        if marker_boundary != expected_boundary or marker.live_send_gate_digest != expected_gate or marker.delivery_witness_digest != expected_delivery:
            return _report(SendFenceDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "marker boundary drift", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if len({marker.family_id for marker in markers}) < min_family_count:
        return _report(SendFenceDecisionKind.HOLD_PENDING_DELIVERY, False, True, "low marker family diversity", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    if len({marker.path_family_id for marker in markers}) < min_path_family_count:
        return _report(SendFenceDecisionKind.HOLD_PENDING_DELIVERY, False, True, "low marker path-family diversity", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
    return _report(SendFenceDecisionKind.ACCEPT_DELIVERED_FENCE, True, False, "send fence accepted", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, markers=markers)
