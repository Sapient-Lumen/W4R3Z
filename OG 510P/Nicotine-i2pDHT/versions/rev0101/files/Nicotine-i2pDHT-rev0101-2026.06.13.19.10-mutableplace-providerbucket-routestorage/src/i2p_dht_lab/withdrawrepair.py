"""rev0063 withdraw/repair publication memory.

Withdraw repair can become locally terminal only after retry settlement says the
withdraw side settled.  This lane keeps the publication/withdraw memory separate
from retry settlement itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

WITHDRAW_REPAIR_DOMAIN = DOMAIN + b":withdraw-repair-v1:"


class WithdrawRepairDecisionKind(str, Enum):
    ACCEPT_WITHDRAW_REPAIR_TERMINAL = "accept_withdraw_repair_terminal"
    HOLD_WITHDRAW_REPAIR_PENDING = "hold_withdraw_repair_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class WithdrawRepairMarker:
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
    live_egress_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(WITHDRAW_REPAIR_DOMAIN + b":marker:" + bencode({
            b"seq": self.sequence, b"prev": self.previous_digest, b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id, b"service": self.service_name, b"scope": self.scope_digest,
            b"request": self.request_digest, b"payload": self.payload_digest, b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key, b"settlement": self.retry_settlement_digest,
            b"egress": self.live_egress_digest, b"family": self.family_id, b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class WithdrawRepairReport:
    decision_kind: WithdrawRepairDecisionKind
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
    retry_idempotency_key: bytes
    retry_settlement_digest: bytes
    live_egress_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def make_withdraw_repair_marker(*, retry_settlement_report: Any, live_egress_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> WithdrawRepairMarker:
    return WithdrawRepairMarker(sequence, previous_digest, SideEffectAction(getattr(retry_settlement_report, "action")), getattr(retry_settlement_report, "profile_id"), getattr(retry_settlement_report, "service_name"), getattr(retry_settlement_report, "scope_digest"), getattr(retry_settlement_report, "request_digest"), getattr(retry_settlement_report, "payload_digest"), getattr(retry_settlement_report, "idempotency_key"), getattr(retry_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(retry_settlement_report), _digest(live_egress_report), family_id, path_family_id, hard_negative_count)


def _report(kind: WithdrawRepairDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, retry_settlement_report: Any, live_egress_report: Any | None, markers: tuple[WithdrawRepairMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> WithdrawRepairReport:
    digests = tuple(marker.marker_digest for marker in markers)
    families = {marker.family_id for marker in markers}
    paths = {marker.path_family_id for marker in markers}
    hard = int(getattr(retry_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(live_egress_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in markers)
    report_digest = sha256(WITHDRAW_REPAIR_DOMAIN + b":report:" + bencode({b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0, b"terminal": 1 if terminal else 0, b"settlement": _digest(retry_settlement_report), b"egress": _digest(live_egress_report), b"markers": list(digests), b"families": len(families), b"paths": len(paths), b"hard": hard}))
    return WithdrawRepairReport(kind, accept, watch, terminal, reason, SideEffectAction(getattr(retry_settlement_report, "action")), getattr(retry_settlement_report, "profile_id"), getattr(retry_settlement_report, "service_name"), getattr(retry_settlement_report, "scope_digest"), getattr(retry_settlement_report, "request_digest"), getattr(retry_settlement_report, "payload_digest"), getattr(retry_settlement_report, "idempotency_key"), getattr(retry_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(retry_settlement_report), _digest(live_egress_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_withdraw_repair(*, retry_settlement_report: Any, live_egress_report: Any | None = None, markers: Iterable[WithdrawRepairMarker] = (), previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> WithdrawRepairReport:
    marker_tuple = tuple(markers)
    if not bool(getattr(retry_settlement_report, "accept", False)) or bool(getattr(retry_settlement_report, "quarantined", False)) or not bool(getattr(retry_settlement_report, "withdraw_terminal", False)):
        return _report(WithdrawRepairDecisionKind.HOLD_WITHDRAW_REPAIR_PENDING, False, True, False, "withdraw settlement is not terminal", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if live_egress_report is None or not bool(getattr(live_egress_report, "accept", False)) or bool(getattr(live_egress_report, "quarantined", False)) or "withdraw" not in str(getattr(getattr(live_egress_report, "decision_kind", ""), "value", getattr(live_egress_report, "decision_kind", ""))):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "live egress withdraw not accepted", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if _boundary(retry_settlement_report) != _boundary(live_egress_report):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "component boundary drift", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(WithdrawRepairDecisionKind.HOLD_WITHDRAW_REPAIR_PENDING, False, True, False, "withdraw repair marker pending", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    digests = [marker.marker_digest for marker in marker_tuple]
    if any(d in set(seen_marker_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_REPLAY, False, False, False, "withdraw repair replay", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(v) > 1 for v in by_seq.values()):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence withdraw marker fork", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda marker: marker.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(WithdrawRepairDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "previous-link mismatch", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if any(_boundary(marker) != _boundary(retry_settlement_report) or marker.retry_settlement_digest != _digest(retry_settlement_report) or marker.live_egress_digest != _digest(live_egress_report) for marker in marker_tuple):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "marker boundary/digest drift", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if int(getattr(retry_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(live_egress_report, "hard_negative_count", 0) or 0) + sum(marker.hard_negative_count for marker in marker_tuple):
        return _report(WithdrawRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard negative pressure", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if len({marker.family_id for marker in marker_tuple}) < min_family_count:
        return _report(WithdrawRepairDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low family diversity", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    if len({marker.path_family_id for marker in marker_tuple}) < min_path_family_count:
        return _report(WithdrawRepairDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low path diversity", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple)
    return _report(WithdrawRepairDecisionKind.ACCEPT_WITHDRAW_REPAIR_TERMINAL, True, False, True, "withdraw repair publication memory accepted", retry_settlement_report=retry_settlement_report, live_egress_report=live_egress_report, markers=marker_tuple, accepted_marker_digest=marker_tuple[-1].marker_digest)
