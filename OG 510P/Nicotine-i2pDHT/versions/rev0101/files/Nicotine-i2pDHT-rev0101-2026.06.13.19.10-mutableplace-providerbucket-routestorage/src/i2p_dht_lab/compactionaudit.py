"""Compaction audit after terminal receipt and idempotency repair.

rev0059 makes evidence compaction another exact-boundary permission.  Terminal
receipt, idempotency repair, finality, and prune guard may all accept, but a
local compaction batch must still prove it keeps the durable markers and all hard
negative digests that remain relevant to the idempotency boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

COMPACTION_AUDIT_DOMAIN = DOMAIN + b":compaction-audit-v1:"


class CompactionAuditDecisionKind(str, Enum):
    ACCEPT_COMPACTION = "accept_compaction"
    HOLD_PENDING_REPAIR = "hold_pending_repair"
    HOLD_MISSING_PLAN = "hold_missing_plan"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_DROPS_TERMINAL_RECEIPT = "quarantine_drops_terminal_receipt"
    QUARANTINE_DROPS_IDEMPOTENCY_REPAIR = "quarantine_drops_idempotency_repair"
    QUARANTINE_DROPS_FINALITY_OR_PRUNE = "quarantine_drops_finality_or_prune"
    QUARANTINE_DROPS_HARD_NEGATIVE = "quarantine_drops_hard_negative"


@dataclass(frozen=True)
class CompactionAuditPlan:
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    terminal_receipt_digest: bytes
    idempotency_repair_digest: bytes
    finality_digest: bytes
    prune_guard_digest: bytes
    keep_digests: tuple[bytes, ...]
    drop_digests: tuple[bytes, ...]
    hard_negative_digests: tuple[bytes, ...]
    sequence: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name:
            raise ValueError("compaction audit plan needs profile/service")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("terminal_receipt_digest", self.terminal_receipt_digest),
            ("idempotency_repair_digest", self.idempotency_repair_digest),
            ("finality_digest", self.finality_digest),
            ("prune_guard_digest", self.prune_guard_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.keep_digests + self.drop_digests + self.hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("all compaction digests must be 32 bytes")

    @property
    def plan_digest(self) -> bytes:
        return sha256(COMPACTION_AUDIT_DOMAIN + b":plan:" + bencode({
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"terminal": self.terminal_receipt_digest,
            b"repair": self.idempotency_repair_digest,
            b"finality": self.finality_digest,
            b"prune": self.prune_guard_digest,
            b"keep": self.keep_digests,
            b"drop": self.drop_digests,
            b"hard": self.hard_negative_digests,
            b"seq": self.sequence,
        }))


@dataclass(frozen=True)
class CompactionAuditReport:
    decision_kind: CompactionAuditDecisionKind
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
    keep_count: int
    drop_count: int
    hard_negative_count: int
    component_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def assess_compaction_audit(*, compaction_plan: CompactionAuditPlan | None, terminal_receipt_report: Any, idempotency_repair_report: Any, finality_report: Any, prune_guard_report: Any) -> CompactionAuditReport:
    action = SideEffectAction(getattr(terminal_receipt_report, "action"))
    profile_id = getattr(terminal_receipt_report, "profile_id")
    service_name = getattr(terminal_receipt_report, "service_name")
    scope_digest = getattr(terminal_receipt_report, "scope_digest")
    request_digest = getattr(terminal_receipt_report, "request_digest")
    payload_digest = getattr(terminal_receipt_report, "payload_digest")
    idempotency_key = getattr(terminal_receipt_report, "idempotency_key")
    component_digests = (_digest(terminal_receipt_report), _digest(idempotency_repair_report), _digest(finality_report), _digest(prune_guard_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    for label, report in (("terminal receipt", terminal_receipt_report), ("idempotency repair", idempotency_repair_report), ("finality", finality_report), ("prune guard", prune_guard_report)):
        if not _accept(report) or _quarantined(report):
            return _report(CompactionAuditDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, f"{label} did not accept", **common)
    if _watch(idempotency_repair_report) or _watch(terminal_receipt_report):
        return _report(CompactionAuditDecisionKind.HOLD_PENDING_REPAIR, False, True, "terminal receipt or repair still watchful", **common)
    if compaction_plan is None:
        return _report(CompactionAuditDecisionKind.HOLD_MISSING_PLAN, False, True, "missing compaction plan", **common)
    for report in (idempotency_repair_report, finality_report, prune_guard_report):
        for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
            if getattr(report, attr) != expected:
                return _report(CompactionAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"{attr} drift", plan_digest=compaction_plan.plan_digest, **common)
    for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(compaction_plan, attr) != expected:
            return _report(CompactionAuditDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"plan {attr} drift", plan_digest=compaction_plan.plan_digest, **common)
    if compaction_plan.terminal_receipt_digest != component_digests[0] or compaction_plan.idempotency_repair_digest != component_digests[1] or compaction_plan.finality_digest != component_digests[2] or compaction_plan.prune_guard_digest != component_digests[3]:
        return _report(CompactionAuditDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "component digest drift", plan_digest=compaction_plan.plan_digest, **common)
    keep = set(compaction_plan.keep_digests)
    drop = set(compaction_plan.drop_digests)
    hard = set(compaction_plan.hard_negative_digests)
    if compaction_plan.terminal_receipt_digest in drop or compaction_plan.terminal_receipt_digest not in keep:
        return _report(CompactionAuditDecisionKind.QUARANTINE_DROPS_TERMINAL_RECEIPT, False, False, "terminal receipt digest not preserved", plan_digest=compaction_plan.plan_digest, keep_count=len(keep), drop_count=len(drop), hard_negative_count=len(hard), **common)
    if compaction_plan.idempotency_repair_digest in drop or compaction_plan.idempotency_repair_digest not in keep:
        return _report(CompactionAuditDecisionKind.QUARANTINE_DROPS_IDEMPOTENCY_REPAIR, False, False, "idempotency repair digest not preserved", plan_digest=compaction_plan.plan_digest, keep_count=len(keep), drop_count=len(drop), hard_negative_count=len(hard), **common)
    if compaction_plan.finality_digest in drop or compaction_plan.prune_guard_digest in drop:
        return _report(CompactionAuditDecisionKind.QUARANTINE_DROPS_FINALITY_OR_PRUNE, False, False, "finality/prune digest dropped", plan_digest=compaction_plan.plan_digest, keep_count=len(keep), drop_count=len(drop), hard_negative_count=len(hard), **common)
    if hard and not hard.issubset(keep):
        return _report(CompactionAuditDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE, False, False, "hard negative digest not preserved", plan_digest=compaction_plan.plan_digest, keep_count=len(keep), drop_count=len(drop), hard_negative_count=len(hard), **common)
    return _report(CompactionAuditDecisionKind.ACCEPT_COMPACTION, True, False, "compaction audit accepted", plan_digest=compaction_plan.plan_digest, keep_count=len(keep), drop_count=len(drop), hard_negative_count=len(hard), **common)


def _report(kind: CompactionAuditDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], plan_digest: bytes = ZERO_DIGEST, keep_count: int = 0, drop_count: int = 0, hard_negative_count: int = 0) -> CompactionAuditReport:
    digest = sha256(COMPACTION_AUDIT_DOMAIN + b":report:" + bencode({
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
        b"keep": keep_count,
        b"drop": drop_count,
        b"hard": hard_negative_count,
        b"components": component_digests,
    }))
    return CompactionAuditReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, plan_digest, keep_count, drop_count, hard_negative_count, component_digests, digest)
