"""Delivery settlement after live-send, delivery witness, and send fence.

rev0061 stays no-network.  This module models the next local permission after
rev0060: a delivered-looking public-edge write may not become settled merely
because a gate, witness, and fence all passed independently.  Settlement is a
separate exact-boundary observation with its own sequence, previous-link,
ack-digest, diversity, and hard-negative pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DELIVERY_SETTLEMENT_DOMAIN = DOMAIN + b":delivery-settlement-v1:"


class DeliverySettlementDecisionKind(str, Enum):
    ACCEPT_DELIVERY_SETTLED = "accept_delivery_settled"
    HOLD_PENDING_SETTLEMENT = "hold_pending_settlement"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_ACK_CONFLICT = "quarantine_ack_conflict"
    QUARANTINE_TERMINAL_CONFLICT = "quarantine_terminal_conflict"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class DeliverySettlementMarker:
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
    send_fence_digest: bytes
    ack_digest: bytes
    terminal_kind: str
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(DELIVERY_SETTLEMENT_DOMAIN + b":marker:" + bencode({
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
            b"witness": self.delivery_witness_digest,
            b"fence": self.send_fence_digest,
            b"ack": self.ack_digest,
            b"terminal": self.terminal_kind,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class DeliverySettlementReport:
    decision_kind: DeliverySettlementDecisionKind
    accept: bool
    watch: bool
    terminal: bool
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
    send_fence_digest: bytes
    ack_digest: bytes
    accepted_marker_digest: bytes
    marker_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
    )


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component lacks report_digest")


def expected_settlement_ack_digest(delivery_witness_report: Any) -> bytes:
    receipt = getattr(delivery_witness_report, "accepted_receipt_digest", ZERO_DIGEST)
    return sha256(DELIVERY_SETTLEMENT_DOMAIN + b":settle-ack:" + bencode({
        b"witness": getattr(delivery_witness_report, "report_digest"),
        b"receipt": receipt,
        b"payload": getattr(delivery_witness_report, "payload_digest"),
        b"idem": getattr(delivery_witness_report, "idempotency_key"),
    }))


def make_delivery_settlement_marker(*, send_fence_report: Any, delivery_witness_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, terminal_kind: str = "delivered", family_id: str = "family-a", path_family_id: str = "path-a", ack_digest: bytes | None = None, hard_negative_count: int = 0) -> DeliverySettlementMarker:
    return DeliverySettlementMarker(
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(send_fence_report, "action")),
        profile_id=getattr(send_fence_report, "profile_id"),
        service_name=getattr(send_fence_report, "service_name"),
        scope_digest=getattr(send_fence_report, "scope_digest"),
        request_digest=getattr(send_fence_report, "request_digest"),
        payload_digest=getattr(send_fence_report, "payload_digest"),
        idempotency_key=getattr(send_fence_report, "idempotency_key"),
        live_send_gate_digest=getattr(send_fence_report, "live_send_gate_digest"),
        delivery_witness_digest=getattr(delivery_witness_report, "report_digest"),
        send_fence_digest=getattr(send_fence_report, "report_digest"),
        ack_digest=ack_digest if ack_digest is not None else expected_settlement_ack_digest(delivery_witness_report),
        terminal_kind=terminal_kind,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: DeliverySettlementDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, send_fence_report: Any, delivery_witness_report: Any | None, markers: tuple[DeliverySettlementMarker, ...]) -> DeliverySettlementReport:
    marker_digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers if marker.family_id}
    path_families = {marker.path_family_id for marker in markers if marker.path_family_id}
    hard = int(getattr(send_fence_report, "hard_negative_count", 0) or 0) + int(getattr(delivery_witness_report, "hard_negative_count", 0) or 0) if delivery_witness_report is not None else int(getattr(send_fence_report, "hard_negative_count", 0) or 0)
    hard += sum(marker.hard_negative_count for marker in markers)
    ack_digest = expected_settlement_ack_digest(delivery_witness_report) if delivery_witness_report is not None and hasattr(delivery_witness_report, "report_digest") else ZERO_DIGEST
    digest = sha256(DELIVERY_SETTLEMENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"reason": reason,
        b"fence": getattr(send_fence_report, "report_digest"),
        b"witness": getattr(delivery_witness_report, "report_digest", ZERO_DIGEST),
        b"markers": list(marker_digests),
        b"families": len(families),
        b"paths": len(path_families),
        b"hard": hard,
    }))
    return DeliverySettlementReport(kind, accept, watch, terminal, reason, SideEffectAction(getattr(send_fence_report, "action")), getattr(send_fence_report, "profile_id"), getattr(send_fence_report, "service_name"), getattr(send_fence_report, "scope_digest"), getattr(send_fence_report, "request_digest"), getattr(send_fence_report, "payload_digest"), getattr(send_fence_report, "idempotency_key"), getattr(send_fence_report, "live_send_gate_digest", ZERO_DIGEST), _digest(delivery_witness_report), getattr(send_fence_report, "report_digest"), ack_digest, marker_digests[-1] if accept and marker_digests else ZERO_DIGEST, marker_digests, len(families), len(path_families), hard, digest)


def assess_delivery_settlement(*, send_fence_report: Any, delivery_witness_report: Any | None, markers: Iterable[DeliverySettlementMarker], last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> DeliverySettlementReport:
    marker_tuple = tuple(markers)
    if not _accept(send_fence_report) or _quarantined(send_fence_report):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "send fence not accepted", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if delivery_witness_report is None or not _accept(delivery_witness_report) or _quarantined(delivery_witness_report):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "delivery witness not accepted", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if _watch(send_fence_report) or _watch(delivery_witness_report):
        return _report(DeliverySettlementDecisionKind.HOLD_COMPONENT_WATCH, False, True, False, "component watch pressure", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if _boundary(send_fence_report) != _boundary(delivery_witness_report):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "fence/witness boundary drift", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if int(getattr(send_fence_report, "hard_negative_count", 0) or 0) + int(getattr(delivery_witness_report, "hard_negative_count", 0) or 0):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "component hard-negative pressure", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(DeliverySettlementDecisionKind.HOLD_PENDING_SETTLEMENT, False, True, False, "no settlement markers", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    seen = set(seen_marker_digests)
    marker_digests = [marker.marker_digest for marker in marker_tuple]
    if any(digest in seen for digest in marker_digests) or len(set(marker_digests)) != len(marker_digests):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_REPLAY, False, False, False, "settlement marker replay", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if any(marker.sequence < last_sequence for marker in marker_tuple):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, "settlement sequence rollback", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(digests) > 1 for digests in by_seq.values()):
        return _report(DeliverySettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence settlement fork", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda marker: marker.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(DeliverySettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "previous digest mismatch", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    expected_boundary = _boundary(send_fence_report)
    expected_ack = expected_settlement_ack_digest(delivery_witness_report)
    expected_gate = getattr(send_fence_report, "live_send_gate_digest")
    expected_witness = getattr(delivery_witness_report, "report_digest")
    expected_fence = getattr(send_fence_report, "report_digest")
    for marker in marker_tuple:
        marker_boundary = (marker.action, marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)
        if marker_boundary != expected_boundary or marker.live_send_gate_digest != expected_gate or marker.delivery_witness_digest != expected_witness or marker.send_fence_digest != expected_fence:
            return _report(DeliverySettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "marker boundary/component drift", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
        if marker.ack_digest != expected_ack:
            return _report(DeliverySettlementDecisionKind.QUARANTINE_ACK_CONFLICT, False, False, False, "settlement ack digest conflict", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
        if marker.terminal_kind != "delivered":
            return _report(DeliverySettlementDecisionKind.QUARANTINE_TERMINAL_CONFLICT, False, False, False, "non-delivered terminal kind", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
        if marker.hard_negative_count:
            return _report(DeliverySettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "marker hard-negative pressure", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if len({marker.family_id for marker in marker_tuple}) < min_family_count:
        return _report(DeliverySettlementDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low settlement family diversity", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    if len({marker.path_family_id for marker in marker_tuple}) < min_path_family_count:
        return _report(DeliverySettlementDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low settlement path-family diversity", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
    return _report(DeliverySettlementDecisionKind.ACCEPT_DELIVERY_SETTLED, True, False, True, "delivery settlement accepted", send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, markers=marker_tuple)
