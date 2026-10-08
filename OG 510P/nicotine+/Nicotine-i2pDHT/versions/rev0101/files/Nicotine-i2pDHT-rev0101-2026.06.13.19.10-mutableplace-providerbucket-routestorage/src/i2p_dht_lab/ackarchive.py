"""Archive settled delivery evidence after send fencing.

The archive is no-network local memory.  It prevents a settled send from being
forgotten or rebound to a different payload/idempotency boundary after restart.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ACK_ARCHIVE_DOMAIN = DOMAIN + b":ack-archive-v1:"


class AckArchiveDecisionKind(str, Enum):
    ACCEPT_ARCHIVED_DELIVERY = "accept_archived_delivery"
    HOLD_PENDING_ARCHIVE = "hold_pending_archive"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_SETTLEMENT_NOT_ACCEPTED = "quarantine_settlement_not_accepted"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class AckArchiveEntry:
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    delivery_settlement_digest: bytes
    send_fence_digest: bytes
    delivery_witness_digest: bytes
    accepted_marker_digest: bytes
    archive_generation: int
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def entry_digest(self) -> bytes:
        return sha256(ACK_ARCHIVE_DOMAIN + b":entry:" + bencode({
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"settlement": self.delivery_settlement_digest,
            b"fence": self.send_fence_digest,
            b"witness": self.delivery_witness_digest,
            b"marker": self.accepted_marker_digest,
            b"generation": self.archive_generation,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class AckArchiveReport:
    decision_kind: AckArchiveDecisionKind
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
    delivery_settlement_digest: bytes
    send_fence_digest: bytes
    delivery_witness_digest: bytes
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_ack_archive_entry(*, delivery_settlement_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, archive_generation: int = 1, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> AckArchiveEntry:
    return AckArchiveEntry(
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(delivery_settlement_report, "action")),
        profile_id=getattr(delivery_settlement_report, "profile_id"),
        service_name=getattr(delivery_settlement_report, "service_name"),
        scope_digest=getattr(delivery_settlement_report, "scope_digest"),
        request_digest=getattr(delivery_settlement_report, "request_digest"),
        payload_digest=getattr(delivery_settlement_report, "payload_digest"),
        idempotency_key=getattr(delivery_settlement_report, "idempotency_key"),
        delivery_settlement_digest=getattr(delivery_settlement_report, "report_digest"),
        send_fence_digest=getattr(delivery_settlement_report, "send_fence_digest"),
        delivery_witness_digest=getattr(delivery_settlement_report, "delivery_witness_digest"),
        accepted_marker_digest=getattr(delivery_settlement_report, "accepted_marker_digest"),
        archive_generation=archive_generation,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _report(kind: AckArchiveDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, delivery_settlement_report: Any, entries: tuple[AckArchiveEntry, ...]) -> AckArchiveReport:
    entry_digests = tuple(entry.entry_digest for entry in entries)
    families = {entry.family_id for entry in entries if entry.family_id}
    path_families = {entry.path_family_id for entry in entries if entry.path_family_id}
    hard = int(getattr(delivery_settlement_report, "hard_negative_count", 0) or 0) + sum(entry.hard_negative_count for entry in entries)
    digest = sha256(ACK_ARCHIVE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"reason": reason,
        b"settlement": getattr(delivery_settlement_report, "report_digest"),
        b"entries": list(entry_digests),
        b"families": len(families),
        b"paths": len(path_families),
        b"hard": hard,
    }))
    return AckArchiveReport(kind, accept, watch, terminal, reason, SideEffectAction(getattr(delivery_settlement_report, "action")), getattr(delivery_settlement_report, "profile_id"), getattr(delivery_settlement_report, "service_name"), getattr(delivery_settlement_report, "scope_digest"), getattr(delivery_settlement_report, "request_digest"), getattr(delivery_settlement_report, "payload_digest"), getattr(delivery_settlement_report, "idempotency_key"), getattr(delivery_settlement_report, "report_digest"), getattr(delivery_settlement_report, "send_fence_digest", ZERO_DIGEST), getattr(delivery_settlement_report, "delivery_witness_digest", ZERO_DIGEST), entry_digests[-1] if accept and entry_digests else ZERO_DIGEST, entry_digests, len(families), len(path_families), hard, digest)


def assess_ack_archive(*, delivery_settlement_report: Any, entries: Iterable[AckArchiveEntry], last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_entry_digests: Iterable[bytes] = (), prior_payload_digests_for_idempotency: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> AckArchiveReport:
    entry_tuple = tuple(entries)
    if not bool(getattr(delivery_settlement_report, "accept", False)) or bool(getattr(delivery_settlement_report, "watch", False)) or bool(getattr(delivery_settlement_report, "quarantined", False)):
        return _report(AckArchiveDecisionKind.QUARANTINE_SETTLEMENT_NOT_ACCEPTED, False, False, False, "delivery settlement not terminal accepted", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    if int(getattr(delivery_settlement_report, "hard_negative_count", 0) or 0):
        return _report(AckArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "settlement hard-negative pressure", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    prior_payloads = tuple(prior_payload_digests_for_idempotency)
    if prior_payloads and any(payload != getattr(delivery_settlement_report, "payload_digest") for payload in prior_payloads):
        return _report(AckArchiveDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, False, False, "idempotency key previously archived for different payload", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    if not entry_tuple:
        return _report(AckArchiveDecisionKind.HOLD_PENDING_ARCHIVE, False, True, False, "no archive entries", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    seen = set(seen_entry_digests)
    entry_digests = [entry.entry_digest for entry in entry_tuple]
    if any(digest in seen for digest in entry_digests) or len(set(entry_digests)) != len(entry_digests):
        return _report(AckArchiveDecisionKind.QUARANTINE_REPLAY, False, False, False, "archive replay", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    if any(entry.sequence < last_sequence for entry in entry_tuple):
        return _report(AckArchiveDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, "archive sequence rollback", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for entry in entry_tuple:
        by_seq.setdefault(entry.sequence, set()).add(entry.entry_digest)
    if any(len(digests) > 1 for digests in by_seq.values()):
        return _report(AckArchiveDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence archive fork", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    ordered = sorted(entry_tuple, key=lambda entry: entry.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(AckArchiveDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "previous archive digest mismatch", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    expected_boundary = _boundary(delivery_settlement_report)
    expected_settlement = getattr(delivery_settlement_report, "report_digest")
    expected_fence = getattr(delivery_settlement_report, "send_fence_digest")
    expected_witness = getattr(delivery_settlement_report, "delivery_witness_digest")
    expected_marker = getattr(delivery_settlement_report, "accepted_marker_digest")
    for entry in entry_tuple:
        boundary = (entry.action, entry.profile_id, entry.service_name, entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key)
        if boundary != expected_boundary or entry.delivery_settlement_digest != expected_settlement or entry.send_fence_digest != expected_fence or entry.delivery_witness_digest != expected_witness or entry.accepted_marker_digest != expected_marker:
            return _report(AckArchiveDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "archive boundary/component drift", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
        if entry.hard_negative_count:
            return _report(AckArchiveDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "archive hard-negative pressure", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    if len({entry.family_id for entry in entry_tuple}) < min_family_count:
        return _report(AckArchiveDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low archive family diversity", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    if len({entry.path_family_id for entry in entry_tuple}) < min_path_family_count:
        return _report(AckArchiveDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low archive path-family diversity", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
    return _report(AckArchiveDecisionKind.ACCEPT_ARCHIVED_DELIVERY, True, False, True, "ack archive accepted", delivery_settlement_report=delivery_settlement_report, entries=entry_tuple)
