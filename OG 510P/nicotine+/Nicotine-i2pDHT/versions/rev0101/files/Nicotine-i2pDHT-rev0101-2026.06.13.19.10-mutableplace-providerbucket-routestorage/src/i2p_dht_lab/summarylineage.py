"""rev0071 redacted summary lineage after closure handoff import.

Importing a closure handoff is still not permission to create public or garden
summary lineage.  Summary lineage has its own redaction, contradiction-carry,
sequence, and boundary checks.
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

SUMMARY_LINEAGE_DOMAIN = DOMAIN + b":summary-lineage-v1:"


class SummaryLineageKind(str, Enum):
    OPERATOR_LOCAL_SUMMARY = "operator_local_summary"
    GARDEN_WITNESS_SUMMARY = "garden_witness_summary"
    PUBLIC_REDACTED_SUMMARY = "public_redacted_summary"


class SummaryLineageDecisionKind(str, Enum):
    ACCEPT_SUMMARY_LINEAGE = "accept_summary_lineage"
    HOLD_HANDOFF_IMPORT_PENDING = "hold_handoff_import_pending"
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


_KIND_TO_AUDIENCE = {
    SummaryLineageKind.OPERATOR_LOCAL_SUMMARY: ClosureHandoffAudience.LOCAL_OPERATOR,
    SummaryLineageKind.GARDEN_WITNESS_SUMMARY: ClosureHandoffAudience.GARDEN_WITNESS,
    SummaryLineageKind.PUBLIC_REDACTED_SUMMARY: ClosureHandoffAudience.PUBLIC_SUMMARY,
}


@dataclass(frozen=True)
class SummaryLineageEntry:
    kind: SummaryLineageKind
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
    handoff_import_digest: bytes
    handoff_receipt_digest: bytes
    closure_handoff_digest: bytes
    redacted_summary_digest: bytes
    summary_version: int
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def audience(self) -> ClosureHandoffAudience:
        return _KIND_TO_AUDIENCE[SummaryLineageKind(self.kind)]

    @property
    def entry_digest(self) -> bytes:
        return sha256(SUMMARY_LINEAGE_DOMAIN + b":entry:" + bencode({
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
            b"import": self.handoff_import_digest,
            b"receipt": self.handoff_receipt_digest,
            b"handoff": self.closure_handoff_digest,
            b"summary": self.redacted_summary_digest,
            b"version": self.summary_version,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryLineageReport:
    decision_kind: SummaryLineageDecisionKind
    accept: bool
    watch: bool
    summary_lineage_accepted: bool
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_packet_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _entry_boundary(entry: SummaryLineageEntry) -> tuple[Any, ...]:
    return (SideEffectAction(entry.action), entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)


def make_summary_lineage_entry(*, kind: SummaryLineageKind, sequence: int, handoff_import_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_summary_digest: bytes | None = None, summary_version: int = 1, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "summary-lineage-family-a", path_family_id: str = "summary-lineage-path-a", hard_negative_count: int = 0) -> SummaryLineageEntry:
    entry_kind = SummaryLineageKind(kind)
    summary_digest = redacted_summary_digest or sha256(SUMMARY_LINEAGE_DOMAIN + b":summary:" + _digest(handoff_import_report) + b":" + entry_kind.value.encode() + b":" + str(summary_version).encode())
    contradiction = bool(getattr(handoff_import_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return SummaryLineageEntry(
        kind=entry_kind,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(handoff_import_report, "action")),
        profile_id=getattr(handoff_import_report, "profile_id"),
        service_name=getattr(handoff_import_report, "service_name"),
        scope_digest=getattr(handoff_import_report, "scope_digest"),
        request_digest=getattr(handoff_import_report, "request_digest"),
        payload_digest=getattr(handoff_import_report, "payload_digest"),
        idempotency_key=getattr(handoff_import_report, "idempotency_key"),
        retry_idempotency_key=getattr(handoff_import_report, "retry_idempotency_key", ZERO_DIGEST),
        handoff_import_digest=_digest(handoff_import_report),
        handoff_receipt_digest=getattr(handoff_import_report, "handoff_receipt_digest", ZERO_DIGEST),
        closure_handoff_digest=getattr(handoff_import_report, "closure_handoff_digest", ZERO_DIGEST),
        redacted_summary_digest=summary_digest,
        summary_version=int(summary_version),
        contradiction_carried=contradiction,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: SummaryLineageDecisionKind, accept: bool, watch: bool, lineage: bool, contradiction: bool, redacted: bool, reason: str, *, handoff_import_report: Any, entries: tuple[SummaryLineageEntry, ...], accepted_entry_digest: bytes = ZERO_DIGEST) -> SummaryLineageReport:
    digests = tuple(entry.entry_digest for entry in entries)
    audiences = tuple(sorted({entry.audience.value for entry in entries}))
    families = {entry.family_id for entry in entries}
    paths = {entry.path_family_id for entry in entries}
    hard = int(getattr(handoff_import_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    report_digest = sha256(SUMMARY_LINEAGE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"lineage": 1 if lineage else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"action": SideEffectAction(getattr(handoff_import_report, "action")).value,
        b"profile": getattr(handoff_import_report, "profile_id"),
        b"service": getattr(handoff_import_report, "service_name"),
        b"scope": getattr(handoff_import_report, "scope_digest"),
        b"request": getattr(handoff_import_report, "request_digest"),
        b"payload": getattr(handoff_import_report, "payload_digest"),
        b"idem": getattr(handoff_import_report, "idempotency_key"),
        b"retry_idem": getattr(handoff_import_report, "retry_idempotency_key", ZERO_DIGEST),
        b"import": _digest(handoff_import_report),
        b"receipt": getattr(handoff_import_report, "handoff_receipt_digest", ZERO_DIGEST),
        b"handoff": getattr(handoff_import_report, "closure_handoff_digest", ZERO_DIGEST),
        b"accepted": accepted_entry_digest,
        b"audiences": list(audiences),
        b"entries": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryLineageReport(kind, accept, watch, lineage, contradiction, redacted, reason, SideEffectAction(getattr(handoff_import_report, "action")), getattr(handoff_import_report, "profile_id"), getattr(handoff_import_report, "service_name"), getattr(handoff_import_report, "scope_digest"), getattr(handoff_import_report, "request_digest"), getattr(handoff_import_report, "payload_digest"), getattr(handoff_import_report, "idempotency_key"), getattr(handoff_import_report, "retry_idempotency_key", ZERO_DIGEST), _digest(handoff_import_report), getattr(handoff_import_report, "handoff_receipt_digest", ZERO_DIGEST), getattr(handoff_import_report, "closure_handoff_digest", ZERO_DIGEST), accepted_entry_digest, audiences, digests, len(families), len(paths), hard, report_digest)


def assess_summary_lineage(*, handoff_import_report: Any, entries: tuple[SummaryLineageEntry, ...], previous_digest: bytes = ZERO_DIGEST, required_audiences: tuple[ClosureHandoffAudience, ...] = (ClosureHandoffAudience.LOCAL_OPERATOR, ClosureHandoffAudience.GARDEN_WITNESS), min_family_count: int = 2, min_path_family_count: int = 2) -> SummaryLineageReport:
    if not (getattr(handoff_import_report, "accept", False) and getattr(handoff_import_report, "handoff_imported", False)):
        return _report(SummaryLineageDecisionKind.HOLD_HANDOFF_IMPORT_PENDING, False, True, False, False, True, "handoff import is not accepted", handoff_import_report=handoff_import_report, entries=entries)
    if not entries:
        return _report(SummaryLineageDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, False, True, "no summary lineage entries", handoff_import_report=handoff_import_report, entries=entries)
    expected_boundary = _boundary(handoff_import_report)
    expected_import = _digest(handoff_import_report)
    expected_receipt = getattr(handoff_import_report, "handoff_receipt_digest", ZERO_DIGEST)
    expected_handoff = getattr(handoff_import_report, "closure_handoff_digest", ZERO_DIGEST)
    seen_seq: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    prev = previous_digest
    contradiction = False
    for entry in sorted(entries, key=lambda item: item.sequence):
        digest = entry.entry_digest
        if digest in seen_digests:
            return _report(SummaryLineageDecisionKind.QUARANTINE_REPLAY, False, True, False, False, False, "duplicate summary lineage entry", handoff_import_report=handoff_import_report, entries=entries)
        seen_digests.add(digest)
        if entry.sequence <= 0:
            return _report(SummaryLineageDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive summary sequence", handoff_import_report=handoff_import_report, entries=entries)
        if entry.sequence in seen_seq and seen_seq[entry.sequence] != digest:
            return _report(SummaryLineageDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence summary fork", handoff_import_report=handoff_import_report, entries=entries)
        seen_seq[entry.sequence] = digest
        if entry.previous_digest != prev:
            return _report(SummaryLineageDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "previous digest mismatch", handoff_import_report=handoff_import_report, entries=entries)
        if _entry_boundary(entry) != expected_boundary:
            return _report(SummaryLineageDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "summary boundary drift", handoff_import_report=handoff_import_report, entries=entries)
        if entry.handoff_import_digest != expected_import or entry.handoff_receipt_digest != expected_receipt or entry.closure_handoff_digest != expected_handoff:
            return _report(SummaryLineageDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", handoff_import_report=handoff_import_report, entries=entries)
        if entry.raw_boundary_exposed or entry.raw_payload_exposed:
            return _report(SummaryLineageDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "summary leaked raw boundary or payload", handoff_import_report=handoff_import_report, entries=entries)
        if entry.hard_negative_count or int(getattr(handoff_import_report, "hard_negative_count", 0) or 0):
            return _report(SummaryLineageDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, bool(entry.contradiction_carried), True, "hard negative pressure", handoff_import_report=handoff_import_report, entries=entries)
        contradiction = contradiction or entry.contradiction_carried
        prev = digest
    if not contradiction:
        return _report(SummaryLineageDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "summary lineage dropped contradiction memory", handoff_import_report=handoff_import_report, entries=entries)
    required = {ClosureHandoffAudience(audience).value for audience in required_audiences}
    actual = {entry.audience.value for entry in entries}
    if not required.issubset(actual):
        return _report(SummaryLineageDecisionKind.HOLD_MISSING_AUDIENCE, False, True, False, True, True, "missing required summary audience", handoff_import_report=handoff_import_report, entries=entries)
    if len({entry.family_id for entry in entries}) < min_family_count:
        return _report(SummaryLineageDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, "low summary family diversity", handoff_import_report=handoff_import_report, entries=entries)
    if len({entry.path_family_id for entry in entries}) < min_path_family_count:
        return _report(SummaryLineageDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, "low summary path diversity", handoff_import_report=handoff_import_report, entries=entries)
    return _report(SummaryLineageDecisionKind.ACCEPT_SUMMARY_LINEAGE, True, False, True, True, True, "summary lineage accepted", handoff_import_report=handoff_import_report, entries=entries, accepted_entry_digest=prev)
