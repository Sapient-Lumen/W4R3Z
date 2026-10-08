"""rev0062 guard between ack pruning and repair/retry debt.

The ACK archive/prune lane says old delivery evidence may be compacted after a
terminal ACK.  The repair lane says missing-ACK evidence must remain sticky until
retry/withdraw/hold is fenced.  This module keeps those permissions from being
mixed across the same public-edge boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_PRUNE_GUARD_DOMAIN = DOMAIN + b":repair-prune-guard-v1:"


class RepairPruneGuardDecisionKind(str, Enum):
    ACCEPT_PRUNE_TERMINAL_ACK = "accept_prune_terminal_ack"
    ACCEPT_RETAIN_REPAIR_DEBT = "accept_retain_repair_debt"
    HOLD_REPAIR_FENCE_PENDING = "hold_repair_fence_pending"
    QUARANTINE_ACK_REPAIR_CONFLICT = "quarantine_ack_repair_conflict"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairPruneGuardReport:
    decision_kind: RepairPruneGuardDecisionKind
    accept: bool
    watch: bool
    prune_allowed: bool
    retain_repair_debt: bool
    retry_fenced: bool
    withdraw_fenced: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    ack_repair_join_digest: bytes
    retry_fence_digest: bytes
    ack_prune_join_digest: bytes
    report_digest: bytes
    family_count: int
    path_family_count: int
    hard_negative_count: int

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


def _family_min(*reports: Any | None) -> int:
    vals = [int(getattr(r, "family_count", 0) or 0) for r in reports if r is not None]
    vals = [v for v in vals if v]
    return min(vals) if vals else 0


def _path_min(*reports: Any | None) -> int:
    vals = [int(getattr(r, "path_family_count", 0) or 0) for r in reports if r is not None]
    vals = [v for v in vals if v]
    return min(vals) if vals else 0


def _hard(*reports: Any | None) -> int:
    return sum(int(getattr(r, "hard_negative_count", 0) or 0) for r in reports if r is not None)


def _report(kind: RepairPruneGuardDecisionKind, accept: bool, watch: bool, prune_allowed: bool, retain_repair_debt: bool, retry_fenced: bool, withdraw_fenced: bool, reason: str, *, ack_repair_join_report: Any, retry_fence_report: Any | None, ack_prune_join_report: Any | None) -> RepairPruneGuardReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(ack_repair_join_report)
    family_count = _family_min(ack_repair_join_report, retry_fence_report, ack_prune_join_report)
    path_family_count = _path_min(ack_repair_join_report, retry_fence_report, ack_prune_join_report)
    hard = _hard(ack_repair_join_report, retry_fence_report, ack_prune_join_report)
    digest = sha256(REPAIR_PRUNE_GUARD_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0,
        b"prune": 1 if prune_allowed else 0, b"retain": 1 if retain_repair_debt else 0,
        b"retry": 1 if retry_fenced else 0, b"withdraw": 1 if withdraw_fenced else 0,
        b"reason": reason, b"join": _digest(ack_repair_join_report), b"fence": _digest(retry_fence_report),
        b"ack_prune": _digest(ack_prune_join_report), b"families": family_count, b"paths": path_family_count, b"hard": hard,
    }))
    return RepairPruneGuardReport(kind, accept, watch, prune_allowed, retain_repair_debt, retry_fenced, withdraw_fenced, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, _digest(ack_repair_join_report), _digest(retry_fence_report), _digest(ack_prune_join_report), digest, family_count, path_family_count, hard)


def assess_repair_prune_guard(*, ack_repair_join_report: Any, retry_fence_report: Any | None = None, ack_prune_join_report: Any | None = None) -> RepairPruneGuardReport:
    reports = (ack_repair_join_report, retry_fence_report, ack_prune_join_report)
    if any(bool(getattr(report, "quarantined", False)) for report in reports if report is not None):
        return _report(RepairPruneGuardDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    if any(report is not None and _boundary(report) != _boundary(ack_repair_join_report) for report in (retry_fence_report, ack_prune_join_report)):
        return _report(RepairPruneGuardDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "component boundary drift", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    if _hard(*reports):
        return _report(RepairPruneGuardDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "hard-negative pressure", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    terminal = bool(getattr(ack_repair_join_report, "terminal", False))
    repair = bool(getattr(ack_repair_join_report, "repair_allowed", False))
    ack_prune_accept = bool(getattr(ack_prune_join_report, "accept", False) and getattr(ack_prune_join_report, "prune_allowed", False)) if ack_prune_join_report is not None else False
    retry_fenced = bool(getattr(retry_fence_report, "retry_fenced", False)) if retry_fence_report is not None else False
    withdraw_fenced = bool(getattr(retry_fence_report, "withdraw_fenced", False)) if retry_fence_report is not None else False
    if terminal and (retry_fenced or withdraw_fenced or repair):
        return _report(RepairPruneGuardDecisionKind.QUARANTINE_ACK_REPAIR_CONFLICT, False, False, False, False, False, False, "terminal ACK conflicts with repair fence", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    if terminal:
        if not ack_prune_accept:
            return _report(RepairPruneGuardDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "terminal ACK lacks accepted prune join", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
        if getattr(ack_repair_join_report, "ack_prune_join_digest", ZERO_DIGEST) != _digest(ack_prune_join_report):
            return _report(RepairPruneGuardDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "ack/repair join does not carry prune digest", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
        return _report(RepairPruneGuardDecisionKind.ACCEPT_PRUNE_TERMINAL_ACK, True, False, True, False, False, False, "terminal ACK evidence may be pruned", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    if repair:
        if retry_fence_report is None or not bool(getattr(retry_fence_report, "accept", False)):
            return _report(RepairPruneGuardDecisionKind.HOLD_REPAIR_FENCE_PENDING, False, True, False, True, False, False, "repair debt waits for retry/withdraw fence", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
        if getattr(retry_fence_report, "ack_repair_join_digest", ZERO_DIGEST) != _digest(ack_repair_join_report):
            return _report(RepairPruneGuardDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "retry fence does not carry ack/repair join digest", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
        return _report(RepairPruneGuardDecisionKind.ACCEPT_RETAIN_REPAIR_DEBT, True, False, False, True, retry_fenced, withdraw_fenced, "repair debt retained after fence", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
    return _report(RepairPruneGuardDecisionKind.HOLD_REPAIR_FENCE_PENDING, False, True, False, True, False, False, "neither terminal ACK nor fenced repair", ack_repair_join_report=ack_repair_join_report, retry_fence_report=retry_fence_report, ack_prune_join_report=ack_prune_join_report)
