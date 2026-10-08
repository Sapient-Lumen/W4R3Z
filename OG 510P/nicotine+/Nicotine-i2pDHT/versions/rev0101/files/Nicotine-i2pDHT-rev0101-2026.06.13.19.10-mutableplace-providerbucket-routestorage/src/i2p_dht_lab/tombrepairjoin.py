"""Tombstone repair join after settlement-store acceptance.

rev0059 treats tombstone repair as a separate post-settlement boundary.  A
settlement store can be locally coherent while tombstone repair still says that
withdrawals, compromise markers, or resurrection blocks have not been carried
through the same pruning/cleanup scope.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

TOMB_REPAIR_JOIN_DOMAIN = DOMAIN + b":tomb-repair-join-v1:"


class TombRepairJoinDecisionKind(str, Enum):
    ACCEPT_NO_TOMBSTONE_DEBT = "accept_no_tombstone_debt"
    ACCEPT_REPAIR_CARRIED = "accept_repair_carried"
    HOLD_MISSING_REPAIR = "hold_missing_repair"
    HOLD_REPAIR_WATCH = "hold_repair_watch"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_RESURRECTION_PRESSURE = "quarantine_resurrection_pressure"
    QUARANTINE_PRUNE_DROPS_REPAIR_EVIDENCE = "quarantine_prune_drops_repair_evidence"
    QUARANTINE_STORE_DIGEST_DRIFT = "quarantine_store_digest_drift"


@dataclass(frozen=True)
class TombRepairJoinReport:
    decision_kind: TombRepairJoinDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    settlement_store_digest: bytes
    tombstone_repair_digest: bytes
    prune_guard_digest: bytes
    expected_live_tombstone_count: int
    carried_tombstone_count: int
    resurrection_count: int
    component_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_entry_digest", "accepted_marker_digest", "plan_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("report lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
    )


def _same_boundary(base: Any, other: Any | None) -> bool:
    return other is None or _boundary(base) == _boundary(other)


def _report(kind: TombRepairJoinDecisionKind, accept: bool, watch: bool, reason: str, *, settlement_store_report: Any, tombstone_repair_report: Any | None, prune_guard_report: Any | None, expected_live_tombstone_count: int) -> TombRepairJoinReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(settlement_store_report)
    components = (_digest(settlement_store_report), _digest(tombstone_repair_report), _digest(prune_guard_report))
    carried = int(getattr(tombstone_repair_report, "carried_tombstone_count", 0) or 0)
    resurrected = int(getattr(tombstone_repair_report, "resurrection_count", 0) or 0)
    digest = sha256(TOMB_REPAIR_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"components": list(components),
        b"expected": expected_live_tombstone_count,
        b"carried": carried,
        b"resurrected": resurrected,
    }))
    return TombRepairJoinReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, _digest(settlement_store_report), _digest(tombstone_repair_report), _digest(prune_guard_report), expected_live_tombstone_count, carried, resurrected, components, digest)


def assess_tomb_repair_join(*, settlement_store_report: Any, tombstone_repair_report: Any | None, prune_guard_report: Any | None, expected_live_tombstone_count: int) -> TombRepairJoinReport:
    if _quarantined(settlement_store_report) or _quarantined(tombstone_repair_report) or _quarantined(prune_guard_report):
        return _report(TombRepairJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if not _accept(settlement_store_report):
        return _report(TombRepairJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "settlement store did not accept", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if not _same_boundary(settlement_store_report, tombstone_repair_report) or not _same_boundary(settlement_store_report, prune_guard_report):
        return _report(TombRepairJoinDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "tomb/prune boundary drift", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if expected_live_tombstone_count <= 0:
        if tombstone_repair_report is not None and int(getattr(tombstone_repair_report, "resurrection_count", 0) or 0) > 0:
            return _report(TombRepairJoinDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, False, False, "resurrection pressure despite zero expected live tombstones", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
        return _report(TombRepairJoinDecisionKind.ACCEPT_NO_TOMBSTONE_DEBT, True, bool(getattr(settlement_store_report, "watch", False)), "no live tombstone debt expected", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if tombstone_repair_report is None:
        return _report(TombRepairJoinDecisionKind.HOLD_MISSING_REPAIR, False, True, "live tombstones expected but no repair report", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if not _accept(tombstone_repair_report) or _watch(tombstone_repair_report):
        return _report(TombRepairJoinDecisionKind.HOLD_REPAIR_WATCH, False, True, "tombstone repair is still watchful", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if int(getattr(tombstone_repair_report, "resurrection_count", 0) or 0) > 0:
        return _report(TombRepairJoinDecisionKind.QUARANTINE_RESURRECTION_PRESSURE, False, False, "tombstone repair reported resurrection pressure", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if int(getattr(tombstone_repair_report, "carried_tombstone_count", 0) or 0) < expected_live_tombstone_count:
        return _report(TombRepairJoinDecisionKind.HOLD_MISSING_REPAIR, False, True, "not all live tombstones carried", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    if prune_guard_report is not None:
        dropped = set(getattr(prune_guard_report, "dropped_digests", ()) or ())
        if _digest(tombstone_repair_report) in dropped:
            return _report(TombRepairJoinDecisionKind.QUARANTINE_PRUNE_DROPS_REPAIR_EVIDENCE, False, False, "prune report dropped tombstone repair evidence", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
    return _report(TombRepairJoinDecisionKind.ACCEPT_REPAIR_CARRIED, True, bool(getattr(settlement_store_report, "watch", False)), "live tombstone repair carried through settlement store", settlement_store_report=settlement_store_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, expected_live_tombstone_count=expected_live_tombstone_count)
