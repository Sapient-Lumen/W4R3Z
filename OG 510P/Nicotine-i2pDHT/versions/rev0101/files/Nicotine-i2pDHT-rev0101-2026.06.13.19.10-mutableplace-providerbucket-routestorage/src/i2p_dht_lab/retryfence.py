"""rev0062 retry/withdraw fence after ack/repair join.

A joined retry decision still is not a rerun button.  The retry path needs
restart-sticky local fence markers carrying the ack/repair join digest and the
live-egress digest, while terminal ACK paths should explicitly hold rather than
turning into retry permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETRY_FENCE_DOMAIN = DOMAIN + b":retry-fence-v1:"


class RetryFenceMarkerKind(str, Enum):
    RETRY_READY = "retry_ready"
    WITHDRAW_READY = "withdraw_ready"
    TERMINAL_ACK_HOLD = "terminal_ack_hold"


class RetryFenceDecisionKind(str, Enum):
    ACCEPT_RETRY_FENCED = "accept_retry_fenced"
    ACCEPT_WITHDRAW_FENCED = "accept_withdraw_fenced"
    HOLD_TERMINAL_ACK_NO_RETRY = "hold_terminal_ack_no_retry"
    HOLD_PENDING_FENCE_MARKER = "hold_pending_fence_marker"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_IDEMPOTENCY_REUSE = "quarantine_idempotency_reuse"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetryFenceMarker:
    kind: RetryFenceMarkerKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    original_idempotency_key: bytes
    retry_idempotency_key: bytes
    ack_repair_join_digest: bytes
    live_egress_digest: bytes
    delivery_repair_digest: bytes
    rollback_probe_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", RetryFenceMarkerKind(self.kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        for name, value in (
            ("previous_digest", self.previous_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest), ("original_idempotency_key", self.original_idempotency_key), ("retry_idempotency_key", self.retry_idempotency_key),
            ("ack_repair_join_digest", self.ack_repair_join_digest), ("live_egress_digest", self.live_egress_digest),
            ("delivery_repair_digest", self.delivery_repair_digest), ("rollback_probe_digest", self.rollback_probe_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family_id:
            raise ValueError("retry fence marker requires profile/service/family/path")

    @property
    def marker_digest(self) -> bytes:
        return sha256(RETRY_FENCE_DOMAIN + b":marker:" + bencode({
            b"kind": self.kind.value, b"seq": self.sequence, b"prev": self.previous_digest,
            b"action": self.action.value, b"profile": self.profile_id, b"service": self.service_name,
            b"scope": self.scope_digest, b"request": self.request_digest, b"payload": self.payload_digest,
            b"orig_idem": self.original_idempotency_key, b"retry_idem": self.retry_idempotency_key,
            b"join": self.ack_repair_join_digest, b"egress": self.live_egress_digest,
            b"repair": self.delivery_repair_digest, b"rollback": self.rollback_probe_digest,
            b"family": self.family_id, b"path_family": self.path_family_id, b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RetryFenceReport:
    decision_kind: RetryFenceDecisionKind
    accept: bool
    watch: bool
    retry_fenced: bool
    withdraw_fenced: bool
    terminal_ack_hold: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    ack_repair_join_digest: bytes
    live_egress_digest: bytes
    delivery_repair_digest: bytes
    rollback_probe_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _report(kind: RetryFenceDecisionKind, accept: bool, watch: bool, retry_fenced: bool, withdraw_fenced: bool, terminal_ack_hold: bool, reason: str, *, ack_repair_join_report: Any, live_egress_report: Any | None, delivery_repair_report: Any | None, rollback_probe_report: Any | None, markers: tuple[RetryFenceMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RetryFenceReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(ack_repair_join_report)
    retry_idem = getattr(ack_repair_join_report, "retry_idempotency_key", ZERO_DIGEST)
    marker_digests = tuple(marker.marker_digest for marker in markers)
    family_count = len({marker.family_id for marker in markers}) if markers else int(getattr(ack_repair_join_report, "family_count", 0) or 0)
    path_family_count = len({marker.path_family_id for marker in markers}) if markers else int(getattr(ack_repair_join_report, "path_family_count", 0) or 0)
    hard = int(getattr(ack_repair_join_report, "hard_negative_count", 0) or 0) + sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (live_egress_report, delivery_repair_report, rollback_probe_report) if component is not None) + sum(marker.hard_negative_count for marker in markers)
    digest = sha256(RETRY_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0,
        b"retry": 1 if retry_fenced else 0, b"withdraw": 1 if withdraw_fenced else 0, b"terminal_hold": 1 if terminal_ack_hold else 0,
        b"reason": reason, b"join": _digest(ack_repair_join_report), b"egress": _digest(live_egress_report),
        b"repair": _digest(delivery_repair_report), b"rollback": _digest(rollback_probe_report), b"markers": list(marker_digests),
        b"families": family_count, b"paths": path_family_count, b"hard": hard,
    }))
    return RetryFenceReport(kind, accept, watch, retry_fenced, withdraw_fenced, terminal_ack_hold, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, retry_idem, _digest(ack_repair_join_report), _digest(live_egress_report), _digest(delivery_repair_report), _digest(rollback_probe_report), accepted_marker_digest, marker_digests, family_count, path_family_count, hard, digest)


def make_retry_fence_marker(*, ack_repair_join_report: Any, live_egress_report: Any | None, delivery_repair_report: Any | None, rollback_probe_report: Any | None, kind: RetryFenceMarkerKind | None = None, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> RetryFenceMarker:
    if kind is None:
        if bool(getattr(ack_repair_join_report, "retry_allowed", False)):
            kind = RetryFenceMarkerKind.RETRY_READY
        elif bool(getattr(ack_repair_join_report, "withdraw_allowed", False)):
            kind = RetryFenceMarkerKind.WITHDRAW_READY
        else:
            kind = RetryFenceMarkerKind.TERMINAL_ACK_HOLD
    return RetryFenceMarker(
        kind=kind,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(ack_repair_join_report, "action")),
        profile_id=getattr(ack_repair_join_report, "profile_id"),
        service_name=getattr(ack_repair_join_report, "service_name"),
        scope_digest=getattr(ack_repair_join_report, "scope_digest"),
        request_digest=getattr(ack_repair_join_report, "request_digest"),
        payload_digest=getattr(ack_repair_join_report, "payload_digest"),
        original_idempotency_key=getattr(ack_repair_join_report, "idempotency_key"),
        retry_idempotency_key=getattr(ack_repair_join_report, "retry_idempotency_key", ZERO_DIGEST),
        ack_repair_join_digest=_digest(ack_repair_join_report),
        live_egress_digest=_digest(live_egress_report),
        delivery_repair_digest=_digest(delivery_repair_report),
        rollback_probe_digest=_digest(rollback_probe_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def assess_retry_fence(*, ack_repair_join_report: Any, live_egress_report: Any | None = None, delivery_repair_report: Any | None = None, rollback_probe_report: Any | None = None, markers: Iterable[RetryFenceMarker] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RetryFenceReport:
    marker_tuple = tuple(markers)
    if bool(getattr(ack_repair_join_report, "quarantined", False)) or any(bool(getattr(component, "quarantined", False)) for component in (live_egress_report, delivery_repair_report, rollback_probe_report) if component is not None):
        return _report(RetryFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "component quarantined", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if bool(getattr(ack_repair_join_report, "terminal", False)):
        if marker_tuple:
            if any(marker.kind is not RetryFenceMarkerKind.TERMINAL_ACK_HOLD for marker in marker_tuple):
                return _report(RetryFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, True, "terminal ACK cannot carry retry/withdraw marker", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        return _report(RetryFenceDecisionKind.HOLD_TERMINAL_ACK_NO_RETRY, False, True, False, False, True, "terminal ACK path holds retry fence", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if not bool(getattr(ack_repair_join_report, "accept", False)):
        return _report(RetryFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "ack/repair join not accepted", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(RetryFenceDecisionKind.HOLD_PENDING_FENCE_MARKER, False, True, False, False, False, "missing retry fence markers", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if getattr(ack_repair_join_report, "retry_idempotency_key", ZERO_DIGEST) == getattr(ack_repair_join_report, "idempotency_key") and bool(getattr(ack_repair_join_report, "retry_allowed", False)):
        return _report(RetryFenceDecisionKind.QUARANTINE_IDEMPOTENCY_REUSE, False, False, False, False, False, "retry idempotency collides with original", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    seen = set(seen_marker_digests)
    by_sequence: dict[int, bytes] = {}
    expected_boundary = _boundary(ack_repair_join_report)
    for marker in marker_tuple:
        if marker.marker_digest in seen:
            return _report(RetryFenceDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "retry fence marker replay", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        marker_boundary = (marker.action, marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.original_idempotency_key)
        if marker_boundary != expected_boundary:
            return _report(RetryFenceDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "retry marker boundary drift", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        if marker.ack_repair_join_digest != _digest(ack_repair_join_report) or marker.live_egress_digest != _digest(live_egress_report) or marker.delivery_repair_digest != _digest(delivery_repair_report) or marker.rollback_probe_digest != _digest(rollback_probe_report):
            return _report(RetryFenceDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "retry marker component digest drift", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        if marker.hard_negative_count:
            return _report(RetryFenceDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "retry marker hard-negative pressure", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        if marker.retry_idempotency_key == marker.original_idempotency_key and marker.kind is RetryFenceMarkerKind.RETRY_READY:
            return _report(RetryFenceDecisionKind.QUARANTINE_IDEMPOTENCY_REUSE, False, False, False, False, False, "retry marker idempotency reuse", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        if marker.sequence < last_sequence:
            return _report(RetryFenceDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "retry marker sequence rollback", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        prior = by_sequence.get(marker.sequence)
        if prior is not None and prior != marker.marker_digest:
            return _report(RetryFenceDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence retry fence fork", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
        by_sequence[marker.sequence] = marker.marker_digest
    ordered = sorted(marker_tuple, key=lambda marker: marker.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(RetryFenceDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "retry fence previous mismatch", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if len({marker.family_id for marker in marker_tuple}) < min_family_count:
        return _report(RetryFenceDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low retry fence family diversity", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    if len({marker.path_family_id for marker in marker_tuple}) < min_path_family_count:
        return _report(RetryFenceDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low retry fence path diversity", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
    latest = ordered[-1]
    if bool(getattr(ack_repair_join_report, "retry_allowed", False)) and latest.kind is RetryFenceMarkerKind.RETRY_READY:
        return _report(RetryFenceDecisionKind.ACCEPT_RETRY_FENCED, True, False, True, False, False, "retry fence accepted", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple, accepted_marker_digest=latest.marker_digest)
    if bool(getattr(ack_repair_join_report, "withdraw_allowed", False)) and latest.kind is RetryFenceMarkerKind.WITHDRAW_READY:
        return _report(RetryFenceDecisionKind.ACCEPT_WITHDRAW_FENCED, True, False, False, True, False, "withdraw fence accepted", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple, accepted_marker_digest=latest.marker_digest)
    return _report(RetryFenceDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "marker kind does not match ack/repair join", ack_repair_join_report=ack_repair_join_report, live_egress_report=live_egress_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, markers=marker_tuple)
