"""rev0072 summary receipt after redacted summary lineage.

A redacted summary lineage is not recipient receipt.  rev0072 adds a
summary-receipt lane so operator, garden, or public-summary receivers can ACK or
refuse the summary without silently granting archive or prune permission.
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

SUMMARY_RECEIPT_DOMAIN = DOMAIN + b":summary-receipt-v1:"


class SummaryReceiptKind(str, Enum):
    OPERATOR_SUMMARY_ACK = "operator_summary_ack"
    GARDEN_SUMMARY_ACK = "garden_summary_ack"
    PUBLIC_SUMMARY_ACK = "public_summary_ack"
    SUMMARY_REFUSED = "summary_refused"


_KIND_TO_AUDIENCE = {
    SummaryReceiptKind.OPERATOR_SUMMARY_ACK: ClosureHandoffAudience.LOCAL_OPERATOR,
    SummaryReceiptKind.GARDEN_SUMMARY_ACK: ClosureHandoffAudience.GARDEN_WITNESS,
    SummaryReceiptKind.PUBLIC_SUMMARY_ACK: ClosureHandoffAudience.PUBLIC_SUMMARY,
    SummaryReceiptKind.SUMMARY_REFUSED: ClosureHandoffAudience.LOCAL_OPERATOR,
}


class SummaryReceiptDecisionKind(str, Enum):
    ACCEPT_SUMMARY_RECEIPTED = "accept_summary_receipted"
    WATCH_SUMMARY_REFUSAL = "watch_summary_refusal"
    HOLD_SUMMARY_LINEAGE_PENDING = "hold_summary_lineage_pending"
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
class SummaryReceiptEntry:
    kind: SummaryReceiptKind
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
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    handoff_import_digest: bytes
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
    redacted_receipt_digest: bytes
    contradiction_carried: bool
    summary_refused: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def audience(self) -> ClosureHandoffAudience:
        return _KIND_TO_AUDIENCE[SummaryReceiptKind(self.kind)]

    @property
    def entry_digest(self) -> bytes:
        return sha256(SUMMARY_RECEIPT_DOMAIN + b":entry:" + bencode({
            b"kind": SummaryReceiptKind(self.kind).value,
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
            b"summary_lineage": self.summary_lineage_digest,
            b"summary_entry": self.accepted_summary_entry_digest,
            b"import": self.handoff_import_digest,
            b"receipt": self.handoff_receipt_digest,
            b"handoff": self.closure_handoff_digest,
            b"redacted_receipt": self.redacted_receipt_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"refused": 1 if self.summary_refused else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryReceiptReport:
    decision_kind: SummaryReceiptDecisionKind
    accept: bool
    watch: bool
    summary_receipted: bool
    contradiction_carried: bool
    summary_refused: bool
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
    summary_lineage_digest: bytes
    accepted_summary_entry_digest: bytes
    handoff_import_digest: bytes
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
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
    for attr in ("report_digest", "accepted_entry_digest", "accepted_marker_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: SummaryReceiptEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_summary_receipt_entry(*, kind: SummaryReceiptKind, sequence: int, summary_lineage_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_receipt_digest: bytes | None = None, contradiction_carried: bool | None = None, summary_refused: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-receipt-family-a", path_family_id: str = "summary-receipt-path-a", hard_negative_count: int = 0) -> SummaryReceiptEntry:
    entry_kind = SummaryReceiptKind(kind)
    receipt_digest = redacted_receipt_digest or sha256(SUMMARY_RECEIPT_DOMAIN + b":redacted-receipt:" + _digest(summary_lineage_report) + b":" + entry_kind.value.encode())
    contradiction = bool(getattr(summary_lineage_report, "contradiction_carried", False)) if contradiction_carried is None else bool(contradiction_carried)
    refused = entry_kind is SummaryReceiptKind.SUMMARY_REFUSED if summary_refused is None else bool(summary_refused)
    return SummaryReceiptEntry(
        kind=entry_kind,
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_lineage_report, "action")),
        profile_id=getattr(summary_lineage_report, "profile_id"),
        service_name=getattr(summary_lineage_report, "service_name"),
        scope_digest=getattr(summary_lineage_report, "scope_digest"),
        request_digest=getattr(summary_lineage_report, "request_digest"),
        payload_digest=getattr(summary_lineage_report, "payload_digest"),
        idempotency_key=getattr(summary_lineage_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_lineage_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_lineage_digest=_digest(summary_lineage_report),
        accepted_summary_entry_digest=getattr(summary_lineage_report, "accepted_entry_digest", ZERO_DIGEST),
        handoff_import_digest=getattr(summary_lineage_report, "handoff_import_digest", ZERO_DIGEST),
        handoff_receipt_digest=getattr(summary_lineage_report, "handoff_receipt_digest", ZERO_DIGEST),
        closure_handoff_digest=getattr(summary_lineage_report, "closure_handoff_digest", ZERO_DIGEST),
        redacted_receipt_digest=receipt_digest,
        contradiction_carried=contradiction,
        summary_refused=refused,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryReceiptDecisionKind, accept: bool, watch: bool, receipted: bool, contradiction: bool, refused: bool, redacted: bool, reason: str, *, summary_lineage_report: Any, entries: tuple[SummaryReceiptEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> SummaryReceiptReport:
    digests = tuple(entry.entry_digest for entry in entries)
    audiences = tuple(sorted({entry.audience.value for entry in entries}))
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = int(getattr(summary_lineage_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(SUMMARY_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"receipted": 1 if receipted else 0,
        b"contradiction": 1 if contradiction else 0,
        b"refused": 1 if refused else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(summary_lineage_report, "action")).value,
        b"profile": getattr(summary_lineage_report, "profile_id"),
        b"service": getattr(summary_lineage_report, "service_name"),
        b"scope": getattr(summary_lineage_report, "scope_digest"),
        b"request": getattr(summary_lineage_report, "request_digest"),
        b"payload": getattr(summary_lineage_report, "payload_digest"),
        b"idem": getattr(summary_lineage_report, "idempotency_key"),
        b"retry_idem": getattr(summary_lineage_report, "retry_idempotency_key", ZERO_DIGEST),
        b"summary_lineage": _digest(summary_lineage_report),
        b"summary_entry": getattr(summary_lineage_report, "accepted_entry_digest", ZERO_DIGEST),
        b"import": getattr(summary_lineage_report, "handoff_import_digest", ZERO_DIGEST),
        b"receipt": getattr(summary_lineage_report, "handoff_receipt_digest", ZERO_DIGEST),
        b"handoff": getattr(summary_lineage_report, "closure_handoff_digest", ZERO_DIGEST),
        b"accepted_entry": accepted_entry_digest,
        b"audiences": audiences,
        b"entries": digests,
        b"families": sorted(families),
        b"paths": sorted(paths),
        b"hard": hard,
    }))
    return SummaryReceiptReport(
        kind, accept, watch, receipted, contradiction, refused, redacted, reason,
        SideEffectAction(getattr(summary_lineage_report, "action")),
        getattr(summary_lineage_report, "profile_id"),
        getattr(summary_lineage_report, "service_name"),
        getattr(summary_lineage_report, "scope_digest"),
        getattr(summary_lineage_report, "request_digest"),
        getattr(summary_lineage_report, "payload_digest"),
        getattr(summary_lineage_report, "idempotency_key"),
        getattr(summary_lineage_report, "retry_idempotency_key", ZERO_DIGEST),
        _digest(summary_lineage_report),
        getattr(summary_lineage_report, "accepted_entry_digest", ZERO_DIGEST),
        getattr(summary_lineage_report, "handoff_import_digest", ZERO_DIGEST),
        getattr(summary_lineage_report, "handoff_receipt_digest", ZERO_DIGEST),
        getattr(summary_lineage_report, "closure_handoff_digest", ZERO_DIGEST),
        accepted_entry_digest,
        audiences,
        digests,
        len(families),
        len(paths),
        hard,
        report_digest,
    )


def assess_summary_receipts(*, summary_lineage_report: Any, entries: tuple[SummaryReceiptEntry, ...], previous_digest: bytes = ZERO_DIGEST, required_audiences: tuple[ClosureHandoffAudience, ...] = (ClosureHandoffAudience.LOCAL_OPERATOR, ClosureHandoffAudience.GARDEN_WITNESS), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryReceiptReport:
    if not (getattr(summary_lineage_report, "accept", False) and getattr(summary_lineage_report, "summary_lineage_accepted", False)):
        return _report(SummaryReceiptDecisionKind.HOLD_SUMMARY_LINEAGE_PENDING, False, True, False, False, False, True, "summary lineage is not accepted", summary_lineage_report=summary_lineage_report, entries=entries)
    if not entries:
        return _report(SummaryReceiptDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, False, False, True, "no summary receipt entries", summary_lineage_report=summary_lineage_report, entries=entries)
    expected_boundary = _boundary(summary_lineage_report)
    expected_summary = _digest(summary_lineage_report)
    expected_entry = getattr(summary_lineage_report, "accepted_entry_digest", ZERO_DIGEST)
    expected_import = getattr(summary_lineage_report, "handoff_import_digest", ZERO_DIGEST)
    expected_receipt = getattr(summary_lineage_report, "handoff_receipt_digest", ZERO_DIGEST)
    expected_handoff = getattr(summary_lineage_report, "closure_handoff_digest", ZERO_DIGEST)
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    prev = previous_digest
    contradiction = False
    refused = False
    for entry in sorted(entries, key=lambda item: item.sequence):
        digest = entry.entry_digest
        if digest in seen_digests:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, False, "duplicate summary receipt entry", summary_lineage_report=summary_lineage_report, entries=entries)
        seen_digests.add(digest)
        if entry.sequence <= 0:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, False, "non-positive summary receipt sequence", summary_lineage_report=summary_lineage_report, entries=entries)
        if entry.sequence in seen_seq and seen_seq[entry.sequence] != digest:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, False, "same-sequence summary receipt fork", summary_lineage_report=summary_lineage_report, entries=entries)
        seen_seq[entry.sequence] = digest
        if entry.previous_digest != prev:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, False, "previous digest mismatch", summary_lineage_report=summary_lineage_report, entries=entries)
        if _entry_boundary(entry) != expected_boundary:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, False, "summary receipt boundary drift", summary_lineage_report=summary_lineage_report, entries=entries)
        if (entry.summary_lineage_digest != expected_summary or entry.accepted_summary_entry_digest != expected_entry or entry.handoff_import_digest != expected_import or entry.handoff_receipt_digest != expected_receipt or entry.closure_handoff_digest != expected_handoff):
            return _report(SummaryReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, False, "component digest drift", summary_lineage_report=summary_lineage_report, entries=entries)
        if entry.raw_boundary_exposed or entry.raw_payload_exposed:
            return _report(SummaryReceiptDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, False, "summary receipt leaked raw boundary or payload", summary_lineage_report=summary_lineage_report, entries=entries)
        if entry.hard_negative_count or int(getattr(summary_lineage_report, "hard_negative_count", 0) or 0):
            return _report(SummaryReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(entry.contradiction_carried), False, True, "hard negative pressure", summary_lineage_report=summary_lineage_report, entries=entries)
        contradiction = contradiction or entry.contradiction_carried
        refused = refused or entry.summary_refused
        prev = digest
    if not contradiction:
        return _report(SummaryReceiptDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, refused, True, "summary receipt dropped contradiction memory", summary_lineage_report=summary_lineage_report, entries=entries)
    if refused:
        return _report(SummaryReceiptDecisionKind.WATCH_SUMMARY_REFUSAL, False, True, False, True, True, True, "summary recipient refused; hold for local review", summary_lineage_report=summary_lineage_report, entries=entries, accepted_entry_digest=prev)
    required = {ClosureHandoffAudience(audience).value for audience in required_audiences}
    actual = {entry.audience.value for entry in entries}
    if not required.issubset(actual):
        return _report(SummaryReceiptDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, True, False, True, "missing required summary receipt audience", summary_lineage_report=summary_lineage_report, entries=entries)
    if len({entry.family_id for entry in entries}) < min_family_count:
        return _report(SummaryReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, False, True, "low summary receipt family diversity", summary_lineage_report=summary_lineage_report, entries=entries)
    if len({entry.path_family_id for entry in entries}) < min_path_family_count:
        return _report(SummaryReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, False, True, "low summary receipt path diversity", summary_lineage_report=summary_lineage_report, entries=entries)
    return _report(SummaryReceiptDecisionKind.ACCEPT_SUMMARY_RECEIPTED, True, False, True, True, False, True, "summary receipt accepted", summary_lineage_report=summary_lineage_report, entries=entries, accepted_entry_digest=prev)
