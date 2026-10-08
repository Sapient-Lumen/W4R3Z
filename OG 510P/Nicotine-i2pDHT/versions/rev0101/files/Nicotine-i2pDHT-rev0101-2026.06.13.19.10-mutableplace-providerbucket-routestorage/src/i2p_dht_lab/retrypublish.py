"""rev0064 retry-publication staging after retry/withdraw settlement.

Retry or withdraw settlement is not itself permission to stage another public-edge
write.  This lane requires the settlement and egress journal to agree at the
same exact boundary, then records previous-linked staging markers for retry or
withdraw publication.  Late-ACK-aborted retries deliberately suppress retry
publication instead of becoming a quiet resend.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETRY_PUBLISH_DOMAIN = DOMAIN + b":retry-publish-v1:"


class RetryPublishIntentKind(str, Enum):
    RETRY_PUBLIC_RECORD = "retry_public_record"
    WITHDRAW_PUBLIC_RECORD = "withdraw_public_record"


class RetryPublishDecisionKind(str, Enum):
    ACCEPT_RETRY_PUBLICATION_STAGED = "accept_retry_publication_staged"
    ACCEPT_WITHDRAW_PUBLICATION_STAGED = "accept_withdraw_publication_staged"
    HOLD_RETRY_SUPPRESSED_BY_LATE_ACK = "hold_retry_suppressed_by_late_ack"
    HOLD_RETRY_SETTLEMENT_PENDING = "hold_retry_settlement_pending"
    HOLD_PUBLICATION_MARKER_PENDING = "hold_publication_marker_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_INTENT_MISMATCH = "quarantine_intent_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetryPublishMarker:
    intent_kind: RetryPublishIntentKind
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
    retry_settlement_digest: bytes
    egress_journal_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(RETRY_PUBLISH_DOMAIN + b":marker:" + bencode({
            b"intent": self.intent_kind.value,
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
            b"settlement": self.retry_settlement_digest,
            b"journal": self.egress_journal_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RetryPublishReport:
    decision_kind: RetryPublishDecisionKind
    accept: bool
    watch: bool
    staged: bool
    retry_staged: bool
    withdraw_staged: bool
    retry_suppressed: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    retry_settlement_digest: bytes
    egress_journal_digest: bytes
    accepted_marker_digest: bytes
    marker_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RetryPublishMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_retry_publish_marker(*, retry_settlement_report: Any, egress_journal_report: Any, intent_kind: RetryPublishIntentKind, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> RetryPublishMarker:
    return RetryPublishMarker(
        intent_kind=RetryPublishIntentKind(intent_kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(retry_settlement_report, "action")),
        profile_id=getattr(retry_settlement_report, "profile_id"),
        service_name=getattr(retry_settlement_report, "service_name"),
        scope_digest=getattr(retry_settlement_report, "scope_digest"),
        request_digest=getattr(retry_settlement_report, "request_digest"),
        payload_digest=getattr(retry_settlement_report, "payload_digest"),
        idempotency_key=getattr(retry_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(retry_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        retry_settlement_digest=_digest(retry_settlement_report),
        egress_journal_digest=_digest(egress_journal_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RetryPublishDecisionKind, accept: bool, watch: bool, staged: bool, retry_staged: bool, withdraw_staged: bool, retry_suppressed: bool, reason: str, *, retry_settlement_report: Any, egress_journal_report: Any, markers: tuple[RetryPublishMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RetryPublishReport:
    digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(retry_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(egress_journal_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(RETRY_PUBLISH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"staged": 1 if staged else 0,
        b"retry": 1 if retry_staged else 0,
        b"withdraw": 1 if withdraw_staged else 0,
        b"suppressed": 1 if retry_suppressed else 0,
        b"settlement": _digest(retry_settlement_report),
        b"journal": _digest(egress_journal_report),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RetryPublishReport(kind, accept, watch, staged, retry_staged, withdraw_staged, retry_suppressed, reason, SideEffectAction(getattr(retry_settlement_report, "action")), getattr(retry_settlement_report, "profile_id"), getattr(retry_settlement_report, "service_name"), getattr(retry_settlement_report, "scope_digest"), getattr(retry_settlement_report, "request_digest"), getattr(retry_settlement_report, "payload_digest"), getattr(retry_settlement_report, "idempotency_key"), getattr(retry_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(retry_settlement_report), _digest(egress_journal_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_retry_publish(*, retry_settlement_report: Any, egress_journal_report: Any, markers: Iterable[RetryPublishMarker] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RetryPublishReport:
    marker_tuple = tuple(markers)
    if bool(getattr(retry_settlement_report, "quarantined", False)) or bool(getattr(egress_journal_report, "quarantined", False)):
        return _report(RetryPublishDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if not bool(getattr(egress_journal_report, "accept", False)):
        return _report(RetryPublishDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "egress journal not accepted", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if _boundary(retry_settlement_report) != _boundary(egress_journal_report):
        return _report(RetryPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "settlement/journal boundary drift", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if int(getattr(retry_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(egress_journal_report, "hard_negative_count", 0) or 0):
        return _report(RetryPublishDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "hard negative pressure", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if bool(getattr(retry_settlement_report, "aborted_by_late_ack", False)):
        return _report(RetryPublishDecisionKind.HOLD_RETRY_SUPPRESSED_BY_LATE_ACK, False, True, False, False, False, True, "late ACK abort suppresses retry publication", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if bool(getattr(retry_settlement_report, "retry_pending", False)) or not bool(getattr(retry_settlement_report, "terminal", False)):
        return _report(RetryPublishDecisionKind.HOLD_RETRY_SETTLEMENT_PENDING, False, True, False, False, False, False, "retry settlement is not terminal", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    expected_intent: RetryPublishIntentKind | None = None
    expected_kind: RetryPublishDecisionKind | None = None
    if bool(getattr(retry_settlement_report, "retry_terminal", False)):
        expected_intent = RetryPublishIntentKind.RETRY_PUBLIC_RECORD
        expected_kind = RetryPublishDecisionKind.ACCEPT_RETRY_PUBLICATION_STAGED
    elif bool(getattr(retry_settlement_report, "withdraw_terminal", False)):
        expected_intent = RetryPublishIntentKind.WITHDRAW_PUBLIC_RECORD
        expected_kind = RetryPublishDecisionKind.ACCEPT_WITHDRAW_PUBLICATION_STAGED
    if expected_intent is None or expected_kind is None:
        return _report(RetryPublishDecisionKind.HOLD_RETRY_SETTLEMENT_PENDING, False, True, False, False, False, False, "settlement terminal kind needs no retry publication", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(RetryPublishDecisionKind.HOLD_PUBLICATION_MARKER_PENDING, False, True, False, False, False, False, "retry-publication staging marker pending", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    digests = [marker.marker_digest for marker in marker_tuple]
    seen = set(seen_marker_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RetryPublishDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, "retry-publication marker replay", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if any(marker.sequence < last_sequence for marker in marker_tuple):
        return _report(RetryPublishDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, False, "sequence rollback", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RetryPublishDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same-sequence retry-publication fork", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda marker: marker.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RetryPublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous-link mismatch", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if any(_marker_boundary(marker) != _boundary(retry_settlement_report) for marker in marker_tuple):
        return _report(RetryPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "marker boundary drift", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if any(marker.retry_settlement_digest != _digest(retry_settlement_report) or marker.egress_journal_digest != _digest(egress_journal_report) for marker in marker_tuple):
        return _report(RetryPublishDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "marker component digest drift", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if any(marker.intent_kind is not expected_intent for marker in marker_tuple):
        return _report(RetryPublishDecisionKind.QUARANTINE_INTENT_MISMATCH, False, False, False, False, False, False, "marker intent does not match settlement", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if sum(marker.hard_negative_count for marker in marker_tuple):
        return _report(RetryPublishDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "marker hard-negative pressure", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if len({marker.family_id for marker in marker_tuple}) < min_family_count:
        return _report(RetryPublishDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, "low retry-publication family diversity", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    if len({marker.path_family_id for marker in marker_tuple}) < min_path_family_count:
        return _report(RetryPublishDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, "low retry-publication path diversity", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple)
    return _report(expected_kind, True, False, True, expected_intent is RetryPublishIntentKind.RETRY_PUBLIC_RECORD, expected_intent is RetryPublishIntentKind.WITHDRAW_PUBLIC_RECORD, False, "retry-publication staging accepted", retry_settlement_report=retry_settlement_report, egress_journal_report=egress_journal_report, markers=marker_tuple, accepted_marker_digest=ordered[-1].marker_digest)
