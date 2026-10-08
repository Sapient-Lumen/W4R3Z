"""Joined settlement store after rev0058 finality branch split.

rev0059 folds the hidden settlement/attestation/tombstone-repair branchlet into
rev0058's finality/retry/prune lineage.  This module treats that fold as a risk
surface: a finality marker and a settlement entry can each be valid local
observations while disagreeing about whether an effect is terminal, retry-held,
or dead-letter-held.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .finalityledger import FinalityMarkerKind
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .settlementlane import SettlementKind
from .sideeffectjournal import SideEffectAction, SideEffectPhase

SETTLEMENT_STORE_DOMAIN = DOMAIN + b":settlement-store-v1:"


class SettlementStoreDecisionKind(str, Enum):
    ACCEPT_TERMINAL_STORE = "accept_terminal_store"
    ACCEPT_RETRY_HELD_STORE = "accept_retry_held_store"
    ACCEPT_DEAD_LETTER_HELD_STORE = "accept_dead_letter_held_store"
    HOLD_ATTESTATION_WATCH = "hold_attestation_watch"
    HOLD_TOMBSTONE_REPAIR_WATCH = "hold_tombstone_repair_watch"
    HOLD_PRUNE_WATCH = "hold_prune_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_FINALITY_SETTLEMENT_DRIFT = "quarantine_finality_settlement_drift"
    QUARANTINE_RETRY_WITHOUT_ESCROW = "quarantine_retry_without_escrow"
    QUARANTINE_TERMINAL_WITH_PENDING_PRUNE = "quarantine_terminal_with_pending_prune"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SettlementStoreReport:
    decision_kind: SettlementStoreDecisionKind
    accept: bool
    watch: bool
    terminal: bool
    reason: str
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    settlement_kind: SettlementKind | None
    finality_kind: FinalityMarkerKind | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    finality_digest: bytes
    settlement_digest: bytes
    attestation_pack_digest: bytes
    tombstone_repair_digest: bytes
    prune_guard_digest: bytes
    retry_escrow_digest: bytes
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    retry_required: bool
    dead_letter_required: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_pack_digest", "plan_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError(f"component report lacks a 32-byte digest: {report!r}")


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


def _same_boundary(base: Any, components: Iterable[Any | None]) -> bool:
    base_boundary = _boundary(base)
    return all(component is None or _boundary(component) == base_boundary for component in components)


def _families(components: Iterable[Any | None]) -> int:
    counts = [int(getattr(component, "family_count", 0) or 0) for component in components if component is not None]
    counts = [value for value in counts if value > 0]
    return min(counts) if counts else 0


def _path_families(components: Iterable[Any | None]) -> int:
    counts = [int(getattr(component, "path_family_count", 0) or 0) for component in components if component is not None]
    counts = [value for value in counts if value > 0]
    return min(counts) if counts else 0


def _hard_negatives(components: Iterable[Any | None]) -> int:
    return sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)


def _report(kind: SettlementStoreDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, finality_report: Any, settlement_report: Any | None = None, attestation_pack_report: Any | None = None, tombstone_repair_report: Any | None = None, prune_guard_report: Any | None = None, retry_escrow_report: Any | None = None) -> SettlementStoreReport:
    components = (finality_report, settlement_report, attestation_pack_report, tombstone_repair_report, prune_guard_report, retry_escrow_report)
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(finality_report)
    component_digests = tuple(_digest(component) for component in components)
    finality_kind = getattr(finality_report, "marker_kind", None)
    if finality_kind is None:
        marker_decision = getattr(getattr(finality_report, "decision_kind", None), "value", "")
        if "terminal_commit" in marker_decision or "commit" in marker_decision:
            finality_kind = FinalityMarkerKind.TERMINAL_COMMIT
        elif "terminal_abort" in marker_decision or "abort" in marker_decision:
            finality_kind = FinalityMarkerKind.TERMINAL_ABORT
        elif "retry" in marker_decision:
            finality_kind = FinalityMarkerKind.RETRY_PENDING
        elif "dead" in marker_decision:
            finality_kind = FinalityMarkerKind.DEAD_LETTER_HELD
    settlement_kind = getattr(settlement_report, "settlement_kind", None) if settlement_report is not None else None
    digest = sha256(SETTLEMENT_STORE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"components": list(component_digests),
        b"families": _families(components),
        b"paths": _path_families(components),
        b"hard": _hard_negatives(components),
    }))
    return SettlementStoreReport(
        kind,
        accept,
        watch,
        terminal,
        reason,
        action,
        getattr(finality_report, "final_phase", None),
        settlement_kind,
        finality_kind,
        profile_id,
        service_name,
        scope_digest,
        request_digest,
        payload_digest,
        idempotency_key,
        _digest(finality_report),
        _digest(settlement_report),
        _digest(attestation_pack_report),
        _digest(tombstone_repair_report),
        _digest(prune_guard_report),
        _digest(retry_escrow_report),
        component_digests,
        _families(components),
        _path_families(components),
        _hard_negatives(components),
        bool(getattr(finality_report, "retry_required", False) or getattr(settlement_report, "retry_required", False)),
        bool(getattr(finality_report, "dead_letter_required", False) or getattr(settlement_report, "dead_letter_required", False)),
        digest,
    )


def assess_settlement_store(
    *,
    finality_report: Any,
    settlement_report: Any,
    attestation_pack_report: Any | None,
    prune_guard_report: Any,
    tombstone_repair_report: Any | None = None,
    retry_escrow_report: Any | None = None,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SettlementStoreReport:
    components = (finality_report, settlement_report, attestation_pack_report, tombstone_repair_report, prune_guard_report, retry_escrow_report)
    required = (finality_report, settlement_report, prune_guard_report)
    if any(_quarantined(component) for component in components):
        return _report(SettlementStoreDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "component is quarantined", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if not all(_accept(component) for component in required):
        return _report(SettlementStoreDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "required finality/settlement/prune component did not accept", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if attestation_pack_report is not None and not _accept(attestation_pack_report):
        return _report(SettlementStoreDecisionKind.HOLD_ATTESTATION_WATCH, False, True, False, "attestation pack has not accepted", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if tombstone_repair_report is not None and not _accept(tombstone_repair_report):
        return _report(SettlementStoreDecisionKind.HOLD_TOMBSTONE_REPAIR_WATCH, False, True, False, "tombstone repair has not accepted", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if not _same_boundary(finality_report, (settlement_report, attestation_pack_report, tombstone_repair_report, prune_guard_report, retry_escrow_report)):
        return _report(SettlementStoreDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "component boundary drift", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if _families((finality_report, settlement_report, attestation_pack_report, tombstone_repair_report)) < min_family_count:
        return _report(SettlementStoreDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low component family diversity", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if _path_families((finality_report, settlement_report, attestation_pack_report, tombstone_repair_report)) < min_path_family_count:
        return _report(SettlementStoreDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low component path diversity", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)

    settlement_kind = SettlementKind(getattr(settlement_report, "settlement_kind"))
    finality_terminal = bool(getattr(finality_report, "terminal", False))
    finality_watch = bool(getattr(finality_report, "watch", False))
    terminal_settlement = settlement_kind in (SettlementKind.COMMIT_SETTLED, SettlementKind.ABORT_SETTLED)
    retry_required = bool(getattr(finality_report, "retry_required", False) or getattr(settlement_report, "retry_required", False))
    dead_required = bool(getattr(finality_report, "dead_letter_required", False) or getattr(settlement_report, "dead_letter_required", False))
    hard_negative_count = _hard_negatives(components)

    if finality_terminal != terminal_settlement:
        return _report(SettlementStoreDecisionKind.QUARANTINE_FINALITY_SETTLEMENT_DRIFT, False, False, False, "finality and settlement disagree on terminality", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if finality_terminal and (_watch(prune_guard_report) or getattr(prune_guard_report, "decision_kind", None).__class__.__name__.endswith("PruneGuardDecisionKind") and "pending" in getattr(getattr(prune_guard_report, "decision_kind", None), "value", "")):
        return _report(SettlementStoreDecisionKind.QUARANTINE_TERMINAL_WITH_PENDING_PRUNE, False, False, False, "terminal store cannot carry pending prune watch", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if finality_terminal and hard_negative_count:
        return _report(SettlementStoreDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "terminal store has hard negative pressure", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if retry_required and not _accept(retry_escrow_report):
        return _report(SettlementStoreDecisionKind.QUARANTINE_RETRY_WITHOUT_ESCROW, False, False, False, "retry-held settlement lacks retry escrow carry", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if _watch(attestation_pack_report):
        return _report(SettlementStoreDecisionKind.HOLD_ATTESTATION_WATCH, False, True, False, "attestation pack still has watch pressure", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if _watch(tombstone_repair_report):
        return _report(SettlementStoreDecisionKind.HOLD_TOMBSTONE_REPAIR_WATCH, False, True, False, "tombstone repair still has watch pressure", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if finality_terminal:
        if _watch(prune_guard_report):
            return _report(SettlementStoreDecisionKind.HOLD_PRUNE_WATCH, False, True, False, "terminal store still has prune watch pressure", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
        return _report(SettlementStoreDecisionKind.ACCEPT_TERMINAL_STORE, True, False, True, "finality and settlement agree on terminal store", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if retry_required:
        return _report(SettlementStoreDecisionKind.ACCEPT_RETRY_HELD_STORE, True, True, False, "retry-held store carries escrow and dead-letter lineage", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if _watch(prune_guard_report):
        return _report(SettlementStoreDecisionKind.HOLD_PRUNE_WATCH, False, True, False, "prune guard still has watch pressure", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    if dead_required or finality_watch:
        return _report(SettlementStoreDecisionKind.ACCEPT_DEAD_LETTER_HELD_STORE, True, True, False, "dead-letter-held store remains watchful", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
    return _report(SettlementStoreDecisionKind.QUARANTINE_FINALITY_SETTLEMENT_DRIFT, False, False, False, "non-terminal store lacks retry/dead-letter watch reason", finality_report=finality_report, settlement_report=settlement_report, attestation_pack_report=attestation_pack_report, tombstone_repair_report=tombstone_repair_report, prune_guard_report=prune_guard_report, retry_escrow_report=retry_escrow_report)
