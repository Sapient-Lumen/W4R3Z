"""Delivery witness receipts after a no-network live-send gate.

This is not a real network acknowledgement protocol.  It models the evidence a
future live path would need after trying an outbound public send: exact-boundary
acknowledgements, family/path diversity, no replay, no same-sequence fork, and
no payload/session/destination drift.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DELIVERY_WITNESS_DOMAIN = DOMAIN + b":delivery-witness-v1:"


class DeliveryWitnessDecisionKind(str, Enum):
    ACCEPT_DELIVERED = "accept_delivered"
    HOLD_PENDING_ACK = "hold_pending_ack"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_SEND_GATE_NOT_ACCEPTED = "quarantine_send_gate_not_accepted"
    QUARANTINE_RECEIPT_REPLAY = "quarantine_receipt_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_PAYLOAD_ACK_DRIFT = "quarantine_payload_ack_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class DeliveryReceipt:
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
    session_digest: bytes
    destination_digest: bytes
    endpoint_digest: bytes
    ack_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def receipt_digest(self) -> bytes:
        return sha256(DELIVERY_WITNESS_DOMAIN + b":receipt:" + bencode({
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
            b"session": self.session_digest,
            b"destination": self.destination_digest,
            b"endpoint": self.endpoint_digest,
            b"ack": self.ack_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class DeliveryWitnessReport:
    decision_kind: DeliveryWitnessDecisionKind
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
    session_digest: bytes
    destination_digest: bytes
    endpoint_digest: bytes
    accepted_receipt_digest: bytes
    receipt_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def expected_ack_digest(live_send_gate_report: Any) -> bytes:
    return sha256(DELIVERY_WITNESS_DOMAIN + b":ack:" + bencode({
        b"gate": getattr(live_send_gate_report, "report_digest"),
        b"payload": getattr(live_send_gate_report, "payload_digest"),
        b"idem": getattr(live_send_gate_report, "idempotency_key"),
        b"session": getattr(live_send_gate_report, "session_digest", ZERO_DIGEST),
        b"destination": getattr(live_send_gate_report, "destination_digest", ZERO_DIGEST),
        b"endpoint": getattr(live_send_gate_report, "endpoint_digest", ZERO_DIGEST),
    }))


def make_delivery_receipt(*, live_send_gate_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", ack_digest: bytes | None = None, hard_negative_count: int = 0) -> DeliveryReceipt:
    return DeliveryReceipt(
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
        session_digest=getattr(live_send_gate_report, "session_digest", ZERO_DIGEST),
        destination_digest=getattr(live_send_gate_report, "destination_digest", ZERO_DIGEST),
        endpoint_digest=getattr(live_send_gate_report, "endpoint_digest", ZERO_DIGEST),
        ack_digest=ack_digest if ack_digest is not None else expected_ack_digest(live_send_gate_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _boundary_from_gate(gate: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(gate, "action")),
        getattr(gate, "profile_id"),
        getattr(gate, "service_name"),
        getattr(gate, "scope_digest"),
        getattr(gate, "request_digest"),
        getattr(gate, "payload_digest"),
        getattr(gate, "idempotency_key"),
        getattr(gate, "report_digest"),
        getattr(gate, "session_digest", ZERO_DIGEST),
        getattr(gate, "destination_digest", ZERO_DIGEST),
        getattr(gate, "endpoint_digest", ZERO_DIGEST),
    )


def _boundary_from_receipt(receipt: DeliveryReceipt) -> tuple[Any, ...]:
    return (receipt.action, receipt.profile_id, receipt.service_name, receipt.scope_digest, receipt.request_digest, receipt.payload_digest, receipt.idempotency_key, receipt.live_send_gate_digest, receipt.session_digest, receipt.destination_digest, receipt.endpoint_digest)


def _report(kind: DeliveryWitnessDecisionKind, accept: bool, watch: bool, reason: str, *, live_send_gate_report: Any, receipts: tuple[DeliveryReceipt, ...]) -> DeliveryWitnessReport:
    receipt_digests = tuple(receipt.receipt_digest for receipt in receipts)
    families = {receipt.family_id for receipt in receipts if receipt.family_id}
    path_families = {receipt.path_family_id for receipt in receipts if receipt.path_family_id}
    hard = sum(receipt.hard_negative_count for receipt in receipts) + int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0)
    accepted_receipt = receipt_digests[-1] if accept and receipt_digests else ZERO_DIGEST
    digest = sha256(DELIVERY_WITNESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"gate": getattr(live_send_gate_report, "report_digest"),
        b"receipts": list(receipt_digests),
        b"families": len(families),
        b"paths": len(path_families),
        b"hard": hard,
    }))
    return DeliveryWitnessReport(kind, accept, watch, reason, SideEffectAction(getattr(live_send_gate_report, "action")), getattr(live_send_gate_report, "profile_id"), getattr(live_send_gate_report, "service_name"), getattr(live_send_gate_report, "scope_digest"), getattr(live_send_gate_report, "request_digest"), getattr(live_send_gate_report, "payload_digest"), getattr(live_send_gate_report, "idempotency_key"), getattr(live_send_gate_report, "report_digest"), getattr(live_send_gate_report, "session_digest", ZERO_DIGEST), getattr(live_send_gate_report, "destination_digest", ZERO_DIGEST), getattr(live_send_gate_report, "endpoint_digest", ZERO_DIGEST), accepted_receipt, receipt_digests, len(families), len(path_families), hard, digest)


def assess_delivery_witness(*, live_send_gate_report: Any, receipts: Iterable[DeliveryReceipt], last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_receipt_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> DeliveryWitnessReport:
    receipt_tuple = tuple(receipts)
    if not bool(getattr(live_send_gate_report, "accept", False)) or bool(getattr(live_send_gate_report, "watch", False)) or bool(getattr(live_send_gate_report, "quarantined", False)):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_SEND_GATE_NOT_ACCEPTED, False, False, "live-send gate is not terminal accepted", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    if not receipt_tuple:
        return _report(DeliveryWitnessDecisionKind.HOLD_PENDING_ACK, False, True, "no delivery receipts yet", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    seen = set(seen_receipt_digests)
    receipt_digests = [receipt.receipt_digest for receipt in receipt_tuple]
    if any(digest in seen for digest in receipt_digests) or len(set(receipt_digests)) != len(receipt_digests):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_RECEIPT_REPLAY, False, False, "receipt replay", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    if any(receipt.sequence < last_sequence for receipt in receipt_tuple):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "delivery receipt sequence rollback", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for receipt in receipt_tuple:
        by_seq.setdefault(receipt.sequence, set()).add(receipt.receipt_digest)
    if any(len(digests) > 1 for digests in by_seq.values()):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence receipt fork", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    ordered = sorted(receipt_tuple, key=lambda receipt: receipt.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "previous digest mismatch", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    gate_boundary = _boundary_from_gate(live_send_gate_report)
    if any(_boundary_from_receipt(receipt) != gate_boundary for receipt in receipt_tuple):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "receipt boundary drift", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    expected_ack = expected_ack_digest(live_send_gate_report)
    if any(receipt.ack_digest != expected_ack for receipt in receipt_tuple):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_PAYLOAD_ACK_DRIFT, False, False, "delivery ack digest drift", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    if sum(receipt.hard_negative_count for receipt in receipt_tuple) + int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0):
        return _report(DeliveryWitnessDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negative pressure", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    if len({receipt.family_id for receipt in receipt_tuple}) < min_family_count:
        return _report(DeliveryWitnessDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low delivery family diversity", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    if len({receipt.path_family_id for receipt in receipt_tuple}) < min_path_family_count:
        return _report(DeliveryWitnessDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low delivery path-family diversity", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
    return _report(DeliveryWitnessDecisionKind.ACCEPT_DELIVERED, True, False, "delivery witness accepted", live_send_gate_report=live_send_gate_report, receipts=receipt_tuple)
