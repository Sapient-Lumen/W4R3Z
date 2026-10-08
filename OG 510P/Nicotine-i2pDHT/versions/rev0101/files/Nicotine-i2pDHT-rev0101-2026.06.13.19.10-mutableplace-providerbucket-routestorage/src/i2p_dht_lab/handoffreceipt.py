"""rev0071 handoff receipt after redacted closure handoff.

A closure handoff packet is only prepared local evidence.  rev0071 adds a
separate recipient receipt lane so operator/garden/public-summary receivers can
acknowledge or refuse a handoff without turning the prepared handoff into import
permission by accident.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .closurehandoff import ClosureHandoffAudience
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

HANDOFF_RECEIPT_DOMAIN = DOMAIN + b":handoff-receipt-v1:"


class HandoffReceiptKind(str, Enum):
    OPERATOR_ACK = "operator_ack"
    GARDEN_ACK = "garden_ack"
    PUBLIC_SUMMARY_ACK = "public_summary_ack"
    IMPORT_REFUSED = "import_refused"


class HandoffReceiptDecisionKind(str, Enum):
    ACCEPT_HANDOFF_RECEIPTED = "accept_handoff_receipted"
    WATCH_IMPORT_REFUSAL = "watch_import_refusal"
    HOLD_CLOSURE_HANDOFF_PENDING = "hold_closure_handoff_pending"
    HOLD_MISSING_AUDIENCE = "hold_missing_audience"
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
class HandoffReceiptEntry:
    kind: HandoffReceiptKind
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
    closure_handoff_digest: bytes
    accepted_packet_digest: bytes
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    redacted_receipt_digest: bytes
    contradiction_carried: bool
    import_refused: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(HANDOFF_RECEIPT_DOMAIN + b":entry:" + bencode({
            b"kind": self.kind.value,
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
            b"handoff": self.closure_handoff_digest,
            b"packet": self.accepted_packet_digest,
            b"receipt": self.export_receipt_digest,
            b"gc": self.retention_gc_digest,
            b"redacted": self.redacted_receipt_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"import_refused": 1 if self.import_refused else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class HandoffReceiptReport:
    decision_kind: HandoffReceiptDecisionKind
    accept: bool
    watch: bool
    handoff_receipted: bool
    contradiction_carried: bool
    import_refused: bool
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
    closure_handoff_digest: bytes
    accepted_packet_digest: bytes
    export_receipt_digest: bytes
    retention_gc_digest: bytes
    accepted_entry_digest: bytes
    audience_values: tuple[str, ...]
    entry_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_packet_digest", "accepted_entry_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_bundle_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: HandoffReceiptEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_handoff_receipt_entry(*, kind: HandoffReceiptKind, audience: ClosureHandoffAudience, sequence: int, closure_handoff_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_receipt_digest: bytes | None = None, contradiction_carried: bool | None = None, import_refused: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "handoff-receipt-family-a", path_family_id: str = "handoff-receipt-path-a", hard_negative_count: int = 0) -> HandoffReceiptEntry:
    receipt_digest = redacted_receipt_digest or sha256(HANDOFF_RECEIPT_DOMAIN + b":redacted-receipt:" + _digest(closure_handoff_report) + b":" + ClosureHandoffAudience(audience).value.encode() + b":" + HandoffReceiptKind(kind).value.encode())
    refused = HandoffReceiptKind(kind) is HandoffReceiptKind.IMPORT_REFUSED if import_refused is None else bool(import_refused)
    contradiction = bool(getattr(closure_handoff_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    return HandoffReceiptEntry(
        kind=HandoffReceiptKind(kind),
        audience=ClosureHandoffAudience(audience),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(closure_handoff_report, "action")),
        profile_id=getattr(closure_handoff_report, "profile_id"),
        service_name=getattr(closure_handoff_report, "service_name"),
        scope_digest=getattr(closure_handoff_report, "scope_digest"),
        request_digest=getattr(closure_handoff_report, "request_digest"),
        payload_digest=getattr(closure_handoff_report, "payload_digest"),
        idempotency_key=getattr(closure_handoff_report, "idempotency_key"),
        retry_idempotency_key=getattr(closure_handoff_report, "retry_idempotency_key", ZERO_DIGEST),
        closure_handoff_digest=_digest(closure_handoff_report),
        accepted_packet_digest=getattr(closure_handoff_report, "accepted_packet_digest", ZERO_DIGEST),
        export_receipt_digest=getattr(closure_handoff_report, "export_receipt_digest", ZERO_DIGEST),
        retention_gc_digest=getattr(closure_handoff_report, "retention_gc_digest", ZERO_DIGEST),
        redacted_receipt_digest=receipt_digest,
        contradiction_carried=contradiction,
        import_refused=refused,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: HandoffReceiptDecisionKind, accept: bool, watch: bool, receipted: bool, contradiction: bool, refused: bool, redacted: bool, reason: str, *, closure_handoff_report: Any, entries: tuple[HandoffReceiptEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> HandoffReceiptReport:
    digests = tuple(entry.entry_digest for entry in entries)
    audiences = tuple(sorted({entry.audience.value for entry in entries}))
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = int(getattr(closure_handoff_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(HANDOFF_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"receipted": 1 if receipted else 0,
        b"contradiction": 1 if contradiction else 0,
        b"refused": 1 if refused else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(closure_handoff_report, "action")).value,
        b"profile": getattr(closure_handoff_report, "profile_id"),
        b"service": getattr(closure_handoff_report, "service_name"),
        b"scope": getattr(closure_handoff_report, "scope_digest"),
        b"request": getattr(closure_handoff_report, "request_digest"),
        b"payload": getattr(closure_handoff_report, "payload_digest"),
        b"idem": getattr(closure_handoff_report, "idempotency_key"),
        b"retry_idem": getattr(closure_handoff_report, "retry_idempotency_key", ZERO_DIGEST),
        b"handoff": _digest(closure_handoff_report),
        b"packet": getattr(closure_handoff_report, "accepted_packet_digest", ZERO_DIGEST),
        b"receipt": getattr(closure_handoff_report, "export_receipt_digest", ZERO_DIGEST),
        b"gc": getattr(closure_handoff_report, "retention_gc_digest", ZERO_DIGEST),
        b"accepted": accepted_entry_digest,
        b"audiences": list(audiences),
        b"entries": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return HandoffReceiptReport(kind, accept, watch, receipted, contradiction, refused, redacted, reason, SideEffectAction(getattr(closure_handoff_report, "action")), getattr(closure_handoff_report, "profile_id"), getattr(closure_handoff_report, "service_name"), getattr(closure_handoff_report, "scope_digest"), getattr(closure_handoff_report, "request_digest"), getattr(closure_handoff_report, "payload_digest"), getattr(closure_handoff_report, "idempotency_key"), getattr(closure_handoff_report, "retry_idempotency_key", ZERO_DIGEST), _digest(closure_handoff_report), getattr(closure_handoff_report, "accepted_packet_digest", ZERO_DIGEST), getattr(closure_handoff_report, "export_receipt_digest", ZERO_DIGEST), getattr(closure_handoff_report, "retention_gc_digest", ZERO_DIGEST), accepted_entry_digest, audiences, digests, len(families), len(paths), hard, report_digest)


def assess_handoff_receipts(*, closure_handoff_report: Any, entries: tuple[HandoffReceiptEntry, ...], previous_digest: bytes = ZERO_DIGEST, required_audiences: tuple[ClosureHandoffAudience, ...] = (ClosureHandoffAudience.LOCAL_OPERATOR, ClosureHandoffAudience.GARDEN_WITNESS), min_family_count: int = 2, min_path_family_count: int = 2) -> HandoffReceiptReport:
    if not (getattr(closure_handoff_report, "accept", False) and getattr(closure_handoff_report, "closure_handoff_prepared", False)):
        return _report(HandoffReceiptDecisionKind.HOLD_CLOSURE_HANDOFF_PENDING, False, True, False, False, False, True, "closure handoff report is not accepted", closure_handoff_report=closure_handoff_report, entries=entries)
    if not entries:
        return _report(HandoffReceiptDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, False, False, True, "no receipt entries", closure_handoff_report=closure_handoff_report, entries=entries)
    expected_boundary = _boundary(closure_handoff_report)
    expected_handoff = _digest(closure_handoff_report)
    expected_packet = getattr(closure_handoff_report, "accepted_packet_digest", ZERO_DIGEST)
    expected_receipt = getattr(closure_handoff_report, "export_receipt_digest", ZERO_DIGEST)
    expected_gc = getattr(closure_handoff_report, "retention_gc_digest", ZERO_DIGEST)
    seen_by_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    prev = previous_digest
    for entry in sorted(entries, key=lambda item: item.sequence):
        digest = entry.entry_digest
        if digest in seen_digests:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, False, "duplicate receipt entry digest", closure_handoff_report=closure_handoff_report, entries=entries)
        seen_digests.add(digest)
        if entry.sequence <= 0:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, False, "non-positive sequence", closure_handoff_report=closure_handoff_report, entries=entries)
        if entry.sequence in seen_by_seq and seen_by_seq[entry.sequence] != digest:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, False, "same-sequence handoff receipt fork", closure_handoff_report=closure_handoff_report, entries=entries)
        seen_by_seq[entry.sequence] = digest
        if entry.previous_digest != prev:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, False, "previous digest mismatch", closure_handoff_report=closure_handoff_report, entries=entries)
        if _entry_boundary(entry) != expected_boundary:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, False, "receipt boundary drift", closure_handoff_report=closure_handoff_report, entries=entries)
        if entry.closure_handoff_digest != expected_handoff or entry.accepted_packet_digest != expected_packet or entry.export_receipt_digest != expected_receipt or entry.retention_gc_digest != expected_gc:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, False, "component digest drift", closure_handoff_report=closure_handoff_report, entries=entries)
        if entry.raw_boundary_exposed or entry.raw_payload_exposed:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, False, "receipt exposed raw boundary or payload", closure_handoff_report=closure_handoff_report, entries=entries)
        if not entry.contradiction_carried:
            return _report(HandoffReceiptDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, True, "receipt dropped contradiction memory", closure_handoff_report=closure_handoff_report, entries=entries)
        if entry.hard_negative_count or int(getattr(closure_handoff_report, "hard_negative_count", 0) or 0):
            return _report(HandoffReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, entry.import_refused, True, "hard negative pressure", closure_handoff_report=closure_handoff_report, entries=entries)
        prev = digest
    if any(entry.import_refused for entry in entries):
        return _report(HandoffReceiptDecisionKind.WATCH_IMPORT_REFUSAL, False, True, False, True, True, True, "recipient refused import", closure_handoff_report=closure_handoff_report, entries=entries)
    required = {ClosureHandoffAudience(audience).value for audience in required_audiences}
    actual = {entry.audience.value for entry in entries}
    if not required.issubset(actual):
        return _report(HandoffReceiptDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, True, False, True, "missing required receipt audience", closure_handoff_report=closure_handoff_report, entries=entries)
    if len({entry.family_id for entry in entries}) < min_family_count:
        return _report(HandoffReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, False, True, "low receipt family diversity", closure_handoff_report=closure_handoff_report, entries=entries)
    if len({entry.path_family_id for entry in entries}) < min_path_family_count:
        return _report(HandoffReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, False, True, "low receipt path diversity", closure_handoff_report=closure_handoff_report, entries=entries)
    return _report(HandoffReceiptDecisionKind.ACCEPT_HANDOFF_RECEIPTED, True, False, True, True, False, True, "handoff receipt accepted", closure_handoff_report=closure_handoff_report, entries=entries, accepted_entry_digest=prev)
