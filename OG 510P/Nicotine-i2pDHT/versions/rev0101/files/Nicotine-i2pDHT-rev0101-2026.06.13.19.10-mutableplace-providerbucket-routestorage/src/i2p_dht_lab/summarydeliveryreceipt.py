"""rev0075 redacted-summary delivery receipts.

The send canary is still a no-network readiness marker.  Delivery receipts model
what later local evidence should look like after a future redacted summary send:
ACK, refusal, or pending.  Refusal/pending is watch pressure, not success.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_DELIVERY_DOMAIN = DOMAIN + b":summary-delivery-receipt-v1:"


class SummaryDeliveryReceiptKind(str, Enum):
    ACK = "ack"
    REFUSAL = "refusal"
    PENDING = "pending"


class SummaryDeliveryDecisionKind(str, Enum):
    ACCEPT_SUMMARY_DELIVERED = "accept_summary_delivered"
    ACCEPT_REFUSAL_WATCH = "accept_refusal_watch"
    HOLD_PENDING_DELIVERY = "hold_pending_delivery"
    HOLD_CANARY_PENDING = "hold_canary_pending"
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
    QUARANTINE_MIXED_DELIVERY_STATE = "quarantine_mixed_delivery_state"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SummaryDeliveryReceipt:
    receipt_kind: SummaryDeliveryReceiptKind
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
    summary_send_canary_digest: bytes
    accepted_canary_marker_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
    redacted_summary_digest: bytes
    ack_digest: bytes
    refusal_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def receipt_digest(self) -> bytes:
        return sha256(SUMMARY_DELIVERY_DOMAIN + b":receipt:" + bencode({
            b"kind": SummaryDeliveryReceiptKind(self.receipt_kind).value,
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
            b"canary": self.summary_send_canary_digest,
            b"canary_marker": self.accepted_canary_marker_digest,
            b"dest": self.destination_digest,
            b"sam": self.sam_endpoint_digest,
            b"redacted_summary": self.redacted_summary_digest,
            b"ack": self.ack_digest,
            b"refusal": self.refusal_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryDeliveryReport:
    decision_kind: SummaryDeliveryDecisionKind
    accept: bool
    watch: bool
    delivery_confirmed: bool
    refusal_observed: bool
    pending_observed: bool
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
    summary_send_canary_digest: bytes
    accepted_receipt_digest: bytes
    accepted_canary_marker_digest: bytes
    destination_digest: bytes
    sam_endpoint_digest: bytes
    redacted_summary_digest: bytes
    receipt_kinds: tuple[str, ...]
    receipt_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"), getattr(report, "retry_idempotency_key", ZERO_DIGEST))


def _receipt_boundary(receipt: SummaryDeliveryReceipt) -> tuple[Any, ...]:
    return (SideEffectAction(receipt.action), receipt.profile_id, receipt.service_name, receipt.scope_digest, receipt.request_digest, receipt.payload_digest, receipt.idempotency_key, receipt.retry_idempotency_key)


def make_summary_delivery_receipt(*, receipt_kind: SummaryDeliveryReceiptKind, sequence: int, summary_send_canary_report: Any, previous_digest: bytes = ZERO_DIGEST, ack_digest: bytes | None = None, refusal_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-delivery-family-a", path_family_id: str = "summary-delivery-path-a", hard_negative_count: int = 0) -> SummaryDeliveryReceipt:
    kind = SummaryDeliveryReceiptKind(receipt_kind)
    ack = ack_digest or (sha256(SUMMARY_DELIVERY_DOMAIN + b":ack:" + _digest(summary_send_canary_report)) if kind is SummaryDeliveryReceiptKind.ACK else ZERO_DIGEST)
    refusal = refusal_digest or (sha256(SUMMARY_DELIVERY_DOMAIN + b":refusal:" + _digest(summary_send_canary_report)) if kind is SummaryDeliveryReceiptKind.REFUSAL else ZERO_DIGEST)
    contradiction = bool(getattr(summary_send_canary_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    return SummaryDeliveryReceipt(
        receipt_kind=kind,
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_send_canary_report, "action")),
        profile_id=getattr(summary_send_canary_report, "profile_id"),
        service_name=getattr(summary_send_canary_report, "service_name"),
        scope_digest=getattr(summary_send_canary_report, "scope_digest"),
        request_digest=getattr(summary_send_canary_report, "request_digest"),
        payload_digest=getattr(summary_send_canary_report, "payload_digest"),
        idempotency_key=getattr(summary_send_canary_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_send_canary_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_send_canary_digest=_digest(summary_send_canary_report),
        accepted_canary_marker_digest=getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        destination_digest=getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST),
        sam_endpoint_digest=getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST),
        redacted_summary_digest=getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST),
        ack_digest=ack,
        refusal_digest=refusal,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryDeliveryDecisionKind, accept: bool, watch: bool, delivered: bool, refused: bool, pending: bool, contradiction: bool, redacted: bool, reason: str, *, summary_send_canary_report: Any, receipts: tuple[SummaryDeliveryReceipt, ...], accepted_receipt_digest: bytes = ZERO_DIGEST) -> SummaryDeliveryReport:
    families = {receipt.family_id for receipt in receipts}
    paths = {receipt.path_family_id for receipt in receipts}
    receipt_kinds = tuple(sorted({receipt.receipt_kind.value for receipt in receipts}))
    receipt_digests = tuple(receipt.receipt_digest for receipt in receipts)
    hard = int(getattr(summary_send_canary_report, "hard_negative_count", 0) or 0) + sum(receipt.hard_negative_count for receipt in receipts)
    report_digest = sha256(SUMMARY_DELIVERY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"delivered": 1 if delivered else 0,
        b"refused": 1 if refused else 0,
        b"pending": 1 if pending else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_send_canary_report, "action")).value,
        b"profile": getattr(summary_send_canary_report, "profile_id"),
        b"service": getattr(summary_send_canary_report, "service_name"),
        b"scope": getattr(summary_send_canary_report, "scope_digest"),
        b"request": getattr(summary_send_canary_report, "request_digest"),
        b"payload": getattr(summary_send_canary_report, "payload_digest"),
        b"idem": getattr(summary_send_canary_report, "idempotency_key"),
        b"retry_idem": getattr(summary_send_canary_report, "retry_idempotency_key", ZERO_DIGEST),
        b"canary": _digest(summary_send_canary_report),
        b"accepted": accepted_receipt_digest,
        b"canary_marker": getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST),
        b"dest": getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST),
        b"sam": getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST),
        b"redacted_summary": getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST),
        b"receipt_kinds": list(receipt_kinds),
        b"receipts": list(receipt_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryDeliveryReport(kind, accept, watch, delivered, refused, pending, contradiction, redacted, reason, SideEffectAction(getattr(summary_send_canary_report, "action")), getattr(summary_send_canary_report, "profile_id"), getattr(summary_send_canary_report, "service_name"), getattr(summary_send_canary_report, "scope_digest"), getattr(summary_send_canary_report, "request_digest"), getattr(summary_send_canary_report, "payload_digest"), getattr(summary_send_canary_report, "idempotency_key"), getattr(summary_send_canary_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_send_canary_report), accepted_receipt_digest, getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST), getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST), getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST), getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST), receipt_kinds, receipt_digests, len(families), len(paths), hard, report_digest)


def assess_summary_delivery_receipts(*, summary_send_canary_report: Any, receipts: tuple[SummaryDeliveryReceipt, ...], previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryDeliveryReport:
    receipts = tuple(receipts)
    if not getattr(summary_send_canary_report, "canary_ready", False):
        return _report(SummaryDeliveryDecisionKind.HOLD_CANARY_PENDING, False, True, False, False, True, False, True, "summary send canary not ready", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    boundary = _boundary(summary_send_canary_report)
    if any(_receipt_boundary(receipt) != boundary for receipt in receipts):
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, True, False, True, "boundary drift", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    if any(receipt.summary_send_canary_digest != _digest(summary_send_canary_report) or receipt.accepted_canary_marker_digest != getattr(summary_send_canary_report, "accepted_marker_digest", ZERO_DIGEST) or receipt.destination_digest != getattr(summary_send_canary_report, "destination_digest", ZERO_DIGEST) or receipt.sam_endpoint_digest != getattr(summary_send_canary_report, "sam_endpoint_digest", ZERO_DIGEST) or receipt.redacted_summary_digest != getattr(summary_send_canary_report, "redacted_summary_digest", ZERO_DIGEST) for receipt in receipts):
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, True, False, True, "component digest drift", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    if any(receipt.raw_boundary_exposed or receipt.raw_payload_exposed for receipt in receipts):
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, True, False, False, "raw boundary/payload exposure", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    contradiction = bool(getattr(summary_send_canary_report, "contradiction_carried", False) and all(receipt.contradiction_carried for receipt in receipts))
    if not contradiction:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, False, True, "contradiction memory missing", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    hard = int(getattr(summary_send_canary_report, "hard_negative_count", 0) or 0) + sum(receipt.hard_negative_count for receipt in receipts)
    if hard:
        return _report(SummaryDeliveryDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, False, True, True, True, "hard-negative pressure", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    digest_seen: set[bytes] = set()
    for receipt in sorted(receipts, key=lambda item: item.sequence):
        digest = receipt.receipt_digest
        if digest in digest_seen:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_REPLAY, False, True, False, False, True, True, True, "replayed receipt", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
        digest_seen.add(digest)
        if receipt.sequence <= 0:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, True, True, True, "non-positive sequence", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
        if receipt.sequence in seen and seen[receipt.sequence] != digest:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, True, True, True, "same-sequence fork", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
        seen[receipt.sequence] = digest
        if receipt.previous_digest != prev:
            return _report(SummaryDeliveryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, True, True, True, "previous-link mismatch", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
        prev = digest
    families = {receipt.family_id for receipt in receipts}
    paths = {receipt.path_family_id for receipt in receipts}
    if len(families) < min_family_count:
        return _report(SummaryDeliveryDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, True, True, True, "low family diversity", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    if len(paths) < min_path_family_count:
        return _report(SummaryDeliveryDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, True, True, True, "low path diversity", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
    kinds = {receipt.receipt_kind for receipt in receipts}
    accepted = prev if receipts else ZERO_DIGEST
    if kinds == {SummaryDeliveryReceiptKind.ACK}:
        return _report(SummaryDeliveryDecisionKind.ACCEPT_SUMMARY_DELIVERED, True, False, True, False, False, True, True, "summary delivery ACK accepted", summary_send_canary_report=summary_send_canary_report, receipts=receipts, accepted_receipt_digest=accepted)
    if kinds == {SummaryDeliveryReceiptKind.REFUSAL}:
        return _report(SummaryDeliveryDecisionKind.ACCEPT_REFUSAL_WATCH, True, True, False, True, False, True, True, "delivery refused; watch/backoff", summary_send_canary_report=summary_send_canary_report, receipts=receipts, accepted_receipt_digest=accepted)
    if kinds == {SummaryDeliveryReceiptKind.PENDING}:
        return _report(SummaryDeliveryDecisionKind.HOLD_PENDING_DELIVERY, False, True, False, False, True, True, True, "delivery pending", summary_send_canary_report=summary_send_canary_report, receipts=receipts, accepted_receipt_digest=accepted)
    return _report(SummaryDeliveryDecisionKind.QUARANTINE_MIXED_DELIVERY_STATE, False, True, False, SummaryDeliveryReceiptKind.REFUSAL in kinds, SummaryDeliveryReceiptKind.PENDING in kinds, True, True, "mixed delivery state", summary_send_canary_report=summary_send_canary_report, receipts=receipts)
