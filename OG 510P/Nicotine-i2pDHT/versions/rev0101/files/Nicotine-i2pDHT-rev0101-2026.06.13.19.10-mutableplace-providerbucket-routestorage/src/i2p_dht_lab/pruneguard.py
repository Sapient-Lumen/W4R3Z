"""Prune guard for effect finality and retry escrow evidence.

rev0058 makes evidence deletion an explicit boundary.  Terminal commit/abort may
allow soft retry/dead-letter evidence to be compacted, but unresolved retry or
held dead-letter state must stay sticky.  Hard negatives, idempotency conflicts,
and accepted finality markers are never silently pruned by a local convenience
lane.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .finalityledger import FinalityLedgerDecisionKind
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

PRUNE_GUARD_DOMAIN = DOMAIN + b":prune-guard-v1:"


class PruneGuardDecisionKind(str, Enum):
    ACCEPT_TERMINAL_SOFT_PRUNE = "accept_terminal_soft_prune"
    ACCEPT_PENDING_HOLD = "accept_pending_hold"
    HOLD_MISSING_PLAN = "hold_missing_plan"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DROPS_HARD_NEGATIVE = "quarantine_drops_hard_negative"
    QUARANTINE_DROPS_ACCEPTED_FINALITY = "quarantine_drops_accepted_finality"
    QUARANTINE_DROPS_DEAD_LETTER_WHILE_PENDING = "quarantine_drops_dead_letter_while_pending"
    QUARANTINE_DROPS_RETRY_ESCROW_WHILE_PENDING = "quarantine_drops_retry_escrow_while_pending"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"


@dataclass(frozen=True)
class PrunePlan:
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    keep_digests: tuple[bytes, ...]
    drop_digests: tuple[bytes, ...]
    hard_negative_digests: tuple[bytes, ...]
    accepted_finality_digest: bytes
    dead_letter_digest: bytes
    retry_escrow_digest: bytes
    sequence: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name:
            raise ValueError("prune plan needs profile/service")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("accepted_finality_digest", self.accepted_finality_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("retry_escrow_digest", self.retry_escrow_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.keep_digests + self.drop_digests + self.hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("all plan digests must be 32 bytes")

    @property
    def plan_digest(self) -> bytes:
        return sha256(PRUNE_GUARD_DOMAIN + b":plan:" + bencode({
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"keep": self.keep_digests,
            b"drop": self.drop_digests,
            b"hard": self.hard_negative_digests,
            b"accepted_finality": self.accepted_finality_digest,
            b"dead": self.dead_letter_digest,
            b"retry_escrow": self.retry_escrow_digest,
            b"seq": self.sequence,
        }))


@dataclass(frozen=True)
class PruneGuardReport:
    decision_kind: PruneGuardDecisionKind
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
    plan_digest: bytes
    kept_count: int
    dropped_count: int
    hard_negative_count: int
    component_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component report lacks report_digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def assess_prune_guard(
    *,
    prune_plan: PrunePlan | None,
    finality_report: Any,
    retry_escrow_report: Any | None = None,
    dead_letter_report: Any | None = None,
) -> PruneGuardReport:
    action = SideEffectAction(getattr(finality_report, "action"))
    profile_id = getattr(finality_report, "profile_id")
    service_name = getattr(finality_report, "service_name")
    scope_digest = getattr(finality_report, "scope_digest")
    request_digest = getattr(finality_report, "request_digest")
    payload_digest = getattr(finality_report, "payload_digest")
    idempotency_key = getattr(finality_report, "idempotency_key")
    component_digests = (_digest(finality_report), _digest(retry_escrow_report), _digest(dead_letter_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not _accept(finality_report) or _quarantined(finality_report):
        return _report(PruneGuardDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "finality report did not accept", **common)
    if prune_plan is None:
        return _report(PruneGuardDecisionKind.HOLD_MISSING_PLAN, False, True, "missing prune plan", **common)
    for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(prune_plan, attr) != expected:
            return _report(PruneGuardDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"{attr} drift", plan_digest=prune_plan.plan_digest, **common)
    keep = set(prune_plan.keep_digests)
    drop = set(prune_plan.drop_digests)
    hard = set(prune_plan.hard_negative_digests)
    if hard and not hard.issubset(keep):
        return _report(PruneGuardDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE, False, False, "hard negative digest missing from keep set", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
    if prune_plan.accepted_finality_digest != getattr(finality_report, "accepted_marker_digest", ZERO_DIGEST):
        return _report(PruneGuardDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "accepted finality digest drift", plan_digest=prune_plan.plan_digest, **common)
    if prune_plan.accepted_finality_digest and prune_plan.accepted_finality_digest in drop:
        return _report(PruneGuardDecisionKind.QUARANTINE_DROPS_ACCEPTED_FINALITY, False, False, "accepted finality marker cannot be dropped", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
    pending = bool(getattr(finality_report, "watch", False)) or bool(getattr(finality_report, "retry_required", False)) or bool(getattr(finality_report, "dead_letter_required", False))
    if pending:
        if retry_escrow_report is not None and _accept(retry_escrow_report) and _digest(retry_escrow_report) in drop:
            return _report(PruneGuardDecisionKind.QUARANTINE_DROPS_RETRY_ESCROW_WHILE_PENDING, False, False, "retry escrow cannot be dropped while pending", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
        if dead_letter_report is not None and _digest(dead_letter_report) in drop:
            return _report(PruneGuardDecisionKind.QUARANTINE_DROPS_DEAD_LETTER_WHILE_PENDING, False, False, "dead-letter cannot be dropped while pending", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
        return _report(PruneGuardDecisionKind.ACCEPT_PENDING_HOLD, True, True, "pending state preserved through prune guard", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
    terminal_kind = getattr(finality_report, "decision_kind", None)
    if terminal_kind in (FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT, FinalityLedgerDecisionKind.ACCEPT_TERMINAL_ABORT):
        return _report(PruneGuardDecisionKind.ACCEPT_TERMINAL_SOFT_PRUNE, True, False, "terminal soft prune accepted", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)
    return _report(PruneGuardDecisionKind.HOLD_MISSING_PLAN, False, True, "nonterminal finality needs explicit keep plan", plan_digest=prune_plan.plan_digest, kept_count=len(keep), dropped_count=len(drop), hard_negative_count=len(hard), **common)


def _report(kind: PruneGuardDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], plan_digest: bytes = ZERO_DIGEST, kept_count: int = 0, dropped_count: int = 0, hard_negative_count: int = 0) -> PruneGuardReport:
    digest = sha256(PRUNE_GUARD_DOMAIN + b":report:" + bencode({
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
        b"plan": plan_digest,
        b"kept": kept_count,
        b"dropped": dropped_count,
        b"hard": hard_negative_count,
        b"components": component_digests,
    }))
    return PruneGuardReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, plan_digest, kept_count, dropped_count, hard_negative_count, component_digests, digest)
