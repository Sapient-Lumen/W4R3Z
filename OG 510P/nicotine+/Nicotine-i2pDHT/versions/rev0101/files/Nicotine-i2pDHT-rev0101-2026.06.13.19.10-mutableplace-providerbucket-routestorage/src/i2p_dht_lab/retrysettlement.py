"""rev0063 retry/withdraw settlement after retry fence and late-ACK pressure."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETRY_SETTLEMENT_DOMAIN = DOMAIN + b":retry-settlement-v1:"


class RetrySettlementMarkerKind(str, Enum):
    RETRY_DELIVERED = "retry_delivered"
    RETRY_ABORTED_BY_LATE_ACK = "retry_aborted_by_late_ack"
    WITHDRAW_REPAIRED = "withdraw_repaired"


class RetrySettlementDecisionKind(str, Enum):
    ACCEPT_RETRY_DELIVERED = "accept_retry_delivered"
    ACCEPT_RETRY_ABORTED_BY_LATE_ACK = "accept_retry_aborted_by_late_ack"
    ACCEPT_WITHDRAW_REPAIRED = "accept_withdraw_repaired"
    HOLD_RETRY_PENDING = "hold_retry_pending"
    HOLD_LATE_ACK_PENDING_ABORT_MARKER = "hold_late_ack_pending_abort_marker"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_LATE_ACK_RETRY_CONFLICT = "quarantine_late_ack_retry_conflict"
    QUARANTINE_MARKER_KIND_NOT_ALLOWED = "quarantine_marker_kind_not_allowed"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetrySettlementMarker:
    kind: RetrySettlementMarkerKind
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
    retry_fence_digest: bytes
    live_egress_digest: bytes
    late_ack_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(RETRY_SETTLEMENT_DOMAIN + b":marker:" + bencode({
            b"kind": self.kind.value, b"seq": self.sequence, b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value, b"profile": self.profile_id, b"service": self.service_name,
            b"scope": self.scope_digest, b"request": self.request_digest, b"payload": self.payload_digest,
            b"idem": self.idempotency_key, b"retry_idem": self.retry_idempotency_key,
            b"fence": self.retry_fence_digest, b"egress": self.live_egress_digest,
            b"late_ack": self.late_ack_digest, b"family": self.family_id, b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RetrySettlementReport:
    decision_kind: RetrySettlementDecisionKind
    accept: bool
    watch: bool
    terminal: bool
    retry_terminal: bool
    withdraw_terminal: bool
    aborted_by_late_ack: bool
    retry_pending: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    retry_fence_digest: bytes
    live_egress_digest: bytes
    late_ack_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RetrySettlementMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_retry_settlement_marker(*, retry_fence_report: Any, kind: RetrySettlementMarkerKind, sequence: int, live_egress_report: Any | None = None, late_ack_report: Any | None = None, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> RetrySettlementMarker:
    return RetrySettlementMarker(kind, sequence, previous_digest, SideEffectAction(getattr(retry_fence_report, "action")), getattr(retry_fence_report, "profile_id"), getattr(retry_fence_report, "service_name"), getattr(retry_fence_report, "scope_digest"), getattr(retry_fence_report, "request_digest"), getattr(retry_fence_report, "payload_digest"), getattr(retry_fence_report, "idempotency_key"), getattr(retry_fence_report, "retry_idempotency_key", ZERO_DIGEST), _digest(retry_fence_report), _digest(live_egress_report), _digest(late_ack_report), family_id, path_family_id, hard_negative_count)


def _report(kind: RetrySettlementDecisionKind, accept: bool, watch: bool, terminal: bool, retry_terminal: bool, withdraw_terminal: bool, aborted: bool, pending: bool, reason: str, *, retry_fence_report: Any, live_egress_report: Any | None, late_ack_report: Any | None, markers: tuple[RetrySettlementMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RetrySettlementReport:
    digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(retry_fence_report, "hard_negative_count", 0) or 0) + sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (live_egress_report, late_ack_report) if c is not None) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(RETRY_SETTLEMENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0, b"retry_terminal": 1 if retry_terminal else 0,
        b"withdraw_terminal": 1 if withdraw_terminal else 0, b"aborted": 1 if aborted else 0,
        b"pending": 1 if pending else 0, b"fence": _digest(retry_fence_report),
        b"egress": _digest(live_egress_report), b"late_ack": _digest(late_ack_report),
        b"markers": list(digests), b"families": len(families), b"paths": len(paths), b"hard": hard,
    }))
    return RetrySettlementReport(kind, accept, watch, terminal, retry_terminal, withdraw_terminal, aborted, pending, reason, SideEffectAction(getattr(retry_fence_report, "action")), getattr(retry_fence_report, "profile_id"), getattr(retry_fence_report, "service_name"), getattr(retry_fence_report, "scope_digest"), getattr(retry_fence_report, "request_digest"), getattr(retry_fence_report, "payload_digest"), getattr(retry_fence_report, "idempotency_key"), getattr(retry_fence_report, "retry_idempotency_key", ZERO_DIGEST), _digest(retry_fence_report), _digest(live_egress_report), _digest(late_ack_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_retry_settlement(*, retry_fence_report: Any, live_egress_report: Any | None = None, late_ack_report: Any | None = None, markers: Iterable[RetrySettlementMarker] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RetrySettlementReport:
    marker_tuple = tuple(markers)
    if not bool(getattr(retry_fence_report, "accept", False)) or bool(getattr(retry_fence_report, "quarantined", False)) or bool(getattr(live_egress_report, "quarantined", False)) or bool(getattr(late_ack_report, "quarantined", False)):
        return _report(RetrySettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, False, "component not accepted", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if any(c is not None and _boundary(c) != _boundary(retry_fence_report) for c in (live_egress_report, late_ack_report)):
        return _report(RetrySettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, False, "component boundary drift", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    late_present = bool(getattr(late_ack_report, "late_ack_present", False)) if late_ack_report is not None else False
    if not marker_tuple:
        if late_present:
            return _report(RetrySettlementDecisionKind.HOLD_LATE_ACK_PENDING_ABORT_MARKER, False, True, False, False, False, False, True, "late ACK needs explicit abort marker", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
        return _report(RetrySettlementDecisionKind.HOLD_RETRY_PENDING, False, True, False, False, False, False, True, "retry settlement pending", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    digests = [marker.marker_digest for marker in marker_tuple]
    if any(d in set(seen_marker_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(RetrySettlementDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, False, "marker replay", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if any(marker.sequence < last_sequence for marker in marker_tuple):
        return _report(RetrySettlementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, False, False, "sequence rollback", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(v) > 1 for v in by_seq.values()):
        return _report(RetrySettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, False, "same-sequence marker fork", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda marker: marker.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(RetrySettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, False, "previous-link mismatch", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if any(_marker_boundary(marker) != _boundary(retry_fence_report) or marker.retry_fence_digest != _digest(retry_fence_report) or marker.live_egress_digest != _digest(live_egress_report) or marker.late_ack_digest != _digest(late_ack_report) for marker in marker_tuple):
        return _report(RetrySettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, False, "marker boundary/digest drift", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if int(getattr(retry_fence_report, "hard_negative_count", 0) or 0) + sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (live_egress_report, late_ack_report) if c is not None) + sum(marker.hard_negative_count for marker in marker_tuple):
        return _report(RetrySettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, False, "hard negative pressure", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if len({marker.family_id for marker in marker_tuple}) < min_family_count:
        return _report(RetrySettlementDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, True, "low family diversity", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    if len({marker.path_family_id for marker in marker_tuple}) < min_path_family_count:
        return _report(RetrySettlementDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, True, "low path diversity", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    kinds = {marker.kind for marker in marker_tuple}
    if len(kinds) != 1:
        return _report(RetrySettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, False, "mixed marker kinds", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
    kind = next(iter(kinds))
    accepted_marker = marker_tuple[-1].marker_digest
    if kind is RetrySettlementMarkerKind.RETRY_ABORTED_BY_LATE_ACK:
        if not late_present:
            return _report(RetrySettlementDecisionKind.QUARANTINE_MARKER_KIND_NOT_ALLOWED, False, False, False, False, False, False, False, "abort marker without late ACK", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
        return _report(RetrySettlementDecisionKind.ACCEPT_RETRY_ABORTED_BY_LATE_ACK, True, False, True, False, False, True, False, "retry aborted because original ACK arrived late", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple, accepted_marker_digest=accepted_marker)
    if kind is RetrySettlementMarkerKind.RETRY_DELIVERED:
        if late_present:
            return _report(RetrySettlementDecisionKind.QUARANTINE_LATE_ACK_RETRY_CONFLICT, False, False, False, False, False, False, False, "late ACK conflicts with retry delivered", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
        if not bool(getattr(live_egress_report, "accept", False)) or "retry" not in str(getattr(getattr(live_egress_report, "decision_kind", ""), "value", getattr(live_egress_report, "decision_kind", ""))):
            return _report(RetrySettlementDecisionKind.QUARANTINE_MARKER_KIND_NOT_ALLOWED, False, False, False, False, False, False, False, "retry delivered without retry-ready egress", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
        return _report(RetrySettlementDecisionKind.ACCEPT_RETRY_DELIVERED, True, False, True, True, False, False, False, "retry delivered terminally", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple, accepted_marker_digest=accepted_marker)
    if kind is RetrySettlementMarkerKind.WITHDRAW_REPAIRED:
        if not bool(getattr(live_egress_report, "accept", False)) or "withdraw" not in str(getattr(getattr(live_egress_report, "decision_kind", ""), "value", getattr(live_egress_report, "decision_kind", ""))):
            return _report(RetrySettlementDecisionKind.QUARANTINE_MARKER_KIND_NOT_ALLOWED, False, False, False, False, False, False, False, "withdraw repaired without withdraw-ready egress", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
        return _report(RetrySettlementDecisionKind.ACCEPT_WITHDRAW_REPAIRED, True, False, True, False, True, False, False, "withdraw repair settled", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple, accepted_marker_digest=accepted_marker)
    return _report(RetrySettlementDecisionKind.QUARANTINE_MARKER_KIND_NOT_ALLOWED, False, False, False, False, False, False, False, "unknown marker kind", retry_fence_report=retry_fence_report, live_egress_report=live_egress_report, late_ack_report=late_ack_report, markers=marker_tuple)
