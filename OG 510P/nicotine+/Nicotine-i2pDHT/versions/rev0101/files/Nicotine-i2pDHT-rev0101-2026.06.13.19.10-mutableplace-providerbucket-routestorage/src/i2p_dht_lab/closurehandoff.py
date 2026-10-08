"""rev0070 closure handoff after redacted export receipt and retention GC.

A closed repair trace may be handed to an operator, garden witness, or local
archive, but handoff is not a raw dump.  It must bind to the exact closure
boundary, the accepted export receipt, and the accepted retention-GC report while
keeping raw boundary and payload material out of the exported surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CLOSURE_HANDOFF_DOMAIN = DOMAIN + b":closure-handoff-v1:"


class ClosureHandoffAudience(str, Enum):
    LOCAL_OPERATOR = "local_operator"
    GARDEN_WITNESS = "garden_witness"
    PUBLIC_SUMMARY = "public_summary"


class ClosureHandoffDecisionKind(str, Enum):
    ACCEPT_CLOSURE_HANDOFF_PREPARED = "accept_closure_handoff_prepared"
    HOLD_EXPORT_RECEIPT_PENDING = "hold_export_receipt_pending"
    HOLD_RETENTION_GC_PENDING = "hold_retention_gc_pending"
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
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ClosureHandoffPacket:
    audience: ClosureHandoffAudience
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
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    closure_seal_digest: bytes
    audit_export_digest: bytes
    redacted_packet_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def packet_digest(self) -> bytes:
        return sha256(CLOSURE_HANDOFF_DOMAIN + b":packet:" + bencode({
            b"audience": self.audience.value,
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
            b"receipt": self.export_receipt_digest,
            b"gc": self.retention_gc_digest,
            b"seal": self.closure_seal_digest,
            b"export": self.audit_export_digest,
            b"redacted": self.redacted_packet_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ClosureHandoffReport:
    decision_kind: ClosureHandoffDecisionKind
    accept: bool
    watch: bool
    closure_handoff_prepared: bool
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
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    closure_seal_digest: bytes
    accepted_packet_digest: bytes
    packet_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_packet_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_bundle_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _packet_boundary(packet: ClosureHandoffPacket) -> tuple[Any, ...]:
    return (SideEffectAction(packet.action), packet.profile_id, packet.service_name, packet.scope_digest, packet.request_digest, packet.payload_digest, packet.idempotency_key)


def make_closure_handoff_packet(*, audience: ClosureHandoffAudience, sequence: int, export_receipt_report: Any, retention_gc_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_packet_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "closure-handoff-family-a", path_family_id: str = "closure-handoff-path-a", hard_negative_count: int = 0) -> ClosureHandoffPacket:
    contradiction = bool(getattr(retention_gc_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    packet_digest = redacted_packet_digest or sha256(CLOSURE_HANDOFF_DOMAIN + b":redacted-packet:" + _digest(export_receipt_report) + b":" + _digest(retention_gc_report) + b":" + ClosureHandoffAudience(audience).value.encode())
    return ClosureHandoffPacket(
        audience=ClosureHandoffAudience(audience),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(export_receipt_report, "action")),
        profile_id=getattr(export_receipt_report, "profile_id"),
        service_name=getattr(export_receipt_report, "service_name"),
        scope_digest=getattr(export_receipt_report, "scope_digest"),
        request_digest=getattr(export_receipt_report, "request_digest"),
        payload_digest=getattr(export_receipt_report, "payload_digest"),
        idempotency_key=getattr(export_receipt_report, "idempotency_key"),
        retry_idempotency_key=getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        export_receipt_digest=_digest(export_receipt_report),
        retention_gc_digest=_digest(retention_gc_report),
        closure_seal_digest=getattr(export_receipt_report, "closure_seal_digest", getattr(retention_gc_report, "closure_seal_digest", ZERO_DIGEST)),
        audit_export_digest=getattr(export_receipt_report, "audit_export_digest", ZERO_DIGEST),
        redacted_packet_digest=packet_digest,
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ClosureHandoffDecisionKind, accept: bool, watch: bool, prepared: bool, contradiction: bool, redacted: bool, reason: str, *, export_receipt_report: Any, retention_gc_report: Any, packets: tuple[ClosureHandoffPacket, ...], accepted_packet_digest: bytes = ZERO_DIGEST) -> ClosureHandoffReport:
    digests = tuple(packet.packet_digest for packet in packets)
    families = {packet.family_id for packet in packets}
    paths = {packet.path_family_id for packet in packets}
    hard = int(getattr(export_receipt_report, "hard_negative_count", 0) or 0) + int(getattr(retention_gc_report, "hard_negative_count", 0) or 0) + sum(packet.hard_negative_count for packet in packets)
    report_digest = sha256(CLOSURE_HANDOFF_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"prepared": 1 if prepared else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(export_receipt_report, "action")).value,
        b"profile": getattr(export_receipt_report, "profile_id"),
        b"service": getattr(export_receipt_report, "service_name"),
        b"scope": getattr(export_receipt_report, "scope_digest"),
        b"request": getattr(export_receipt_report, "request_digest"),
        b"payload": getattr(export_receipt_report, "payload_digest"),
        b"idem": getattr(export_receipt_report, "idempotency_key"),
        b"retry_idem": getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST),
        b"receipt": _digest(export_receipt_report),
        b"gc": _digest(retention_gc_report),
        b"seal": getattr(export_receipt_report, "closure_seal_digest", getattr(retention_gc_report, "closure_seal_digest", ZERO_DIGEST)),
        b"accepted": accepted_packet_digest,
        b"packets": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return ClosureHandoffReport(kind, accept, watch, prepared, contradiction, redacted, reason, SideEffectAction(getattr(export_receipt_report, "action")), getattr(export_receipt_report, "profile_id"), getattr(export_receipt_report, "service_name"), getattr(export_receipt_report, "scope_digest"), getattr(export_receipt_report, "request_digest"), getattr(export_receipt_report, "payload_digest"), getattr(export_receipt_report, "idempotency_key"), getattr(export_receipt_report, "retry_idempotency_key", ZERO_DIGEST), _digest(export_receipt_report), _digest(retention_gc_report), getattr(export_receipt_report, "closure_seal_digest", getattr(retention_gc_report, "closure_seal_digest", ZERO_DIGEST)), accepted_packet_digest, digests, len(families), len(paths), hard, report_digest)


def assess_closure_handoff(*, export_receipt_report: Any, retention_gc_report: Any, packets: tuple[ClosureHandoffPacket, ...] = (), previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> ClosureHandoffReport:
    if not bool(getattr(export_receipt_report, "accept", False)) or not bool(getattr(export_receipt_report, "export_receipted", False)):
        return _report(ClosureHandoffDecisionKind.HOLD_EXPORT_RECEIPT_PENDING, False, True, False, False, False, "export receipt not accepted", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if not bool(getattr(retention_gc_report, "accept", False)) or not bool(getattr(retention_gc_report, "retention_gc_applied", False)):
        return _report(ClosureHandoffDecisionKind.HOLD_RETENTION_GC_PENDING, False, True, False, False, False, "retention GC not accepted", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if _boundary(export_receipt_report) != _boundary(retention_gc_report):
        return _report(ClosureHandoffDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "receipt/GC boundary drift", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if not packets:
        return _report(ClosureHandoffDecisionKind.HOLD_RETENTION_GC_PENDING, False, True, False, False, False, "no handoff packets", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    for packet in packets:
        if _packet_boundary(packet) != _boundary(export_receipt_report):
            return _report(ClosureHandoffDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "packet boundary drift", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
        if packet.export_receipt_digest != _digest(export_receipt_report) or packet.retention_gc_digest != _digest(retention_gc_report):
            return _report(ClosureHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "handoff component digest drift", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
        if packet.raw_boundary_exposed or packet.raw_payload_exposed:
            return _report(ClosureHandoffDecisionKind.QUARANTINE_RAW_LEAK, False, False, False, packet.contradiction_carried, False, "handoff leaked raw boundary/payload", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    sorted_packets = sorted(packets, key=lambda packet: packet.sequence)
    last = previous_digest
    by_seq: dict[int, bytes] = {}
    for packet in sorted_packets:
        digest = packet.packet_digest
        if packet.sequence <= 0:
            return _report(ClosureHandoffDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive handoff sequence", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
        if packet.sequence in by_seq:
            if by_seq[packet.sequence] == digest:
                return _report(ClosureHandoffDecisionKind.QUARANTINE_REPLAY, False, False, False, packet.contradiction_carried, True, "duplicate handoff replay", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
            return _report(ClosureHandoffDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, packet.contradiction_carried, True, "same sequence handoff fork", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
        by_seq[packet.sequence] = digest
        if packet.previous_digest != last:
            return _report(ClosureHandoffDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, packet.contradiction_carried, True, "handoff previous digest mismatch", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
        last = digest
    families = {packet.family_id for packet in packets}
    paths = {packet.path_family_id for packet in packets}
    contradiction = any(packet.contradiction_carried for packet in packets)
    if len(families) < min_family_count:
        return _report(ClosureHandoffDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, contradiction, True, "not enough handoff family diversity", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if len(paths) < min_path_family_count:
        return _report(ClosureHandoffDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, contradiction, True, "not enough handoff path diversity", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if bool(getattr(retention_gc_report, "contradiction_preserved", False)) and not contradiction:
        return _report(ClosureHandoffDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, True, "handoff dropped contradiction memory", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    if int(getattr(export_receipt_report, "hard_negative_count", 0) or 0) or int(getattr(retention_gc_report, "hard_negative_count", 0) or 0) or any(packet.hard_negative_count for packet in packets):
        return _report(ClosureHandoffDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, contradiction, True, "live hard-negative pressure on handoff", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets)
    return _report(ClosureHandoffDecisionKind.ACCEPT_CLOSURE_HANDOFF_PREPARED, True, False, True, contradiction, True, "closure handoff prepared", export_receipt_report=export_receipt_report, retention_gc_report=retention_gc_report, packets=packets, accepted_packet_digest=sorted_packets[-1].packet_digest)
