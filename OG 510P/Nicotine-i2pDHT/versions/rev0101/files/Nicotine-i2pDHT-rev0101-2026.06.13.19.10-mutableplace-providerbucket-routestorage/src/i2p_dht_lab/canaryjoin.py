"""Canary join after settlement/prune/tombstone repair.

rev0059 keeps canary-style no-network side-effect rehearsals from outrunning the
post-reconcile store.  A SAM/router canary may be valid, but it still must bind
to the exact settlement-store and tombstone-repair state that says the local
side effect is terminal or retry-held.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CANARY_JOIN_DOMAIN = DOMAIN + b":canary-join-v1:"


class CanaryJoinDecisionKind(str, Enum):
    ACCEPT_TERMINAL_CANARY_READY = "accept_terminal_canary_ready"
    ACCEPT_RETRY_CANARY_READY = "accept_retry_canary_ready"
    HOLD_STORE_WATCH = "hold_store_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_TERMINAL_HAS_RETRY_ESCROW = "quarantine_terminal_has_retry_escrow"
    QUARANTINE_RETRY_WITHOUT_ESCROW = "quarantine_retry_without_escrow"
    QUARANTINE_CANARY_WITHOUT_TOMB_JOIN = "quarantine_canary_without_tomb_join"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class CanaryJoinReport:
    decision_kind: CanaryJoinDecisionKind
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
    tomb_repair_join_digest: bytes
    retry_escrow_digest: bytes
    sam_canary_digest: bytes
    router_canary_digest: bytes
    component_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_canary_digest", "accepted_observation_digest", "accepted_ticket_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


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


def _min_count(attr: str, components: Iterable[Any | None]) -> int:
    values = [int(getattr(component, attr, 0) or 0) for component in components if component is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _hard_negatives(components: Iterable[Any | None]) -> int:
    return sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)


def _report(kind: CanaryJoinDecisionKind, accept: bool, watch: bool, reason: str, *, settlement_store_report: Any, tomb_repair_join_report: Any | None = None, retry_escrow_report: Any | None = None, sam_canary_report: Any | None = None, router_canary_report: Any | None = None) -> CanaryJoinReport:
    components = (settlement_store_report, tomb_repair_join_report, retry_escrow_report, sam_canary_report, router_canary_report)
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(settlement_store_report)
    component_digests = tuple(_digest(component) for component in components)
    digest = sha256(CANARY_JOIN_DOMAIN + b":report:" + bencode({
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
        b"components": list(component_digests),
        b"families": _min_count("family_count", components),
        b"paths": _min_count("path_family_count", components),
        b"hard": _hard_negatives(components),
    }))
    return CanaryJoinReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, _digest(settlement_store_report), _digest(tomb_repair_join_report), _digest(retry_escrow_report), _digest(sam_canary_report), _digest(router_canary_report), component_digests, _min_count("family_count", components), _min_count("path_family_count", components), _hard_negatives(components), digest)


def assess_canary_join(*, settlement_store_report: Any, tomb_repair_join_report: Any | None, sam_canary_report: Any | None, router_canary_report: Any | None, retry_escrow_report: Any | None = None, min_family_count: int = 2, min_path_family_count: int = 2) -> CanaryJoinReport:
    components = (settlement_store_report, tomb_repair_join_report, sam_canary_report, router_canary_report, retry_escrow_report)
    if any(_quarantined(component) for component in components):
        return _report(CanaryJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if not _accept(settlement_store_report):
        return _report(CanaryJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "settlement store did not accept", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if tomb_repair_join_report is None or not _accept(tomb_repair_join_report):
        return _report(CanaryJoinDecisionKind.QUARANTINE_CANARY_WITHOUT_TOMB_JOIN, False, False, "canary attempted without accepted tomb-repair join", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if sam_canary_report is None or router_canary_report is None or not _accept(sam_canary_report) or not _accept(router_canary_report):
        return _report(CanaryJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "sam/router canary not accepted", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if not _same_boundary(settlement_store_report, (tomb_repair_join_report, sam_canary_report, router_canary_report, retry_escrow_report)):
        return _report(CanaryJoinDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "canary boundary drift", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if _min_count("family_count", components) < min_family_count:
        return _report(CanaryJoinDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low family diversity", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if _min_count("path_family_count", components) < min_path_family_count:
        return _report(CanaryJoinDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low path diversity", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if _hard_negatives(components):
        return _report(CanaryJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negative pressure blocks canary join", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if bool(getattr(settlement_store_report, "terminal", False)) and retry_escrow_report is not None and _accept(retry_escrow_report):
        return _report(CanaryJoinDecisionKind.QUARANTINE_TERMINAL_HAS_RETRY_ESCROW, False, False, "terminal store unexpectedly carries retry escrow", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if bool(getattr(settlement_store_report, "retry_required", False)) and not _accept(retry_escrow_report):
        return _report(CanaryJoinDecisionKind.QUARANTINE_RETRY_WITHOUT_ESCROW, False, False, "retry canary lacks accepted retry escrow", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    if _watch(settlement_store_report) or _watch(tomb_repair_join_report):
        # Watchful retry is permitted, but remains watchful to prevent a canary
        # from pretending the side effect became terminal.
        return _report(CanaryJoinDecisionKind.ACCEPT_RETRY_CANARY_READY, True, True, "retry/dead-letter store canary ready but watchful", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
    return _report(CanaryJoinDecisionKind.ACCEPT_TERMINAL_CANARY_READY, True, False, "terminal store canary ready", settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, retry_escrow_report=retry_escrow_report, sam_canary_report=sam_canary_report, router_canary_report=router_canary_report)
