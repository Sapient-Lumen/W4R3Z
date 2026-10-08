"""Idempotency repair after terminal receipts.

rev0059 treats an idempotency key as sticky protocol memory.  A terminal receipt
may prove that a local effect settled, but retry/dead-letter lineage can still be
lost if the idempotency table is repaired with the wrong attempt number, wrong
carried dead-letter digest, or wrong component boundary.  This module is a small
no-network algebra for that repair seam.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

IDEMPOTENCY_REPAIR_DOMAIN = DOMAIN + b":idempotency-repair-v1:"


class IdempotencyRepairDecisionKind(str, Enum):
    ACCEPT_TERMINAL_REPAIR = "accept_terminal_repair"
    ACCEPT_RETRY_LINEAGE_REPAIR = "accept_retry_lineage_repair"
    HOLD_MISSING_PLAN = "hold_missing_plan"
    HOLD_TERMINAL_WATCH = "hold_terminal_watch"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_ATTEMPT_REGRESSION = "quarantine_attempt_regression"
    QUARANTINE_MISSING_DEAD_LETTER_CARRY = "quarantine_missing_dead_letter_carry"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class IdempotencyRepairPlan:
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    terminal_receipt_digest: bytes
    finality_digest: bytes
    prune_guard_digest: bytes
    retry_escrow_digest: bytes
    dead_letter_digest: bytes
    carried_dead_letter_digest: bytes
    previous_attempt_number: int
    resolved_attempt_number: int
    sequence: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name:
            raise ValueError("idempotency repair plan needs profile/service")
        if min(self.previous_attempt_number, self.resolved_attempt_number, self.sequence) < 0:
            raise ValueError("attempts and sequence must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("terminal_receipt_digest", self.terminal_receipt_digest),
            ("finality_digest", self.finality_digest),
            ("prune_guard_digest", self.prune_guard_digest),
            ("retry_escrow_digest", self.retry_escrow_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("carried_dead_letter_digest", self.carried_dead_letter_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def plan_digest(self) -> bytes:
        return sha256(IDEMPOTENCY_REPAIR_DOMAIN + b":plan:" + bencode({
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"terminal": self.terminal_receipt_digest,
            b"finality": self.finality_digest,
            b"prune": self.prune_guard_digest,
            b"retry": self.retry_escrow_digest,
            b"dead": self.dead_letter_digest,
            b"carried_dead": self.carried_dead_letter_digest,
            b"prev_attempt": self.previous_attempt_number,
            b"resolved_attempt": self.resolved_attempt_number,
            b"seq": self.sequence,
        }))


@dataclass(frozen=True)
class IdempotencyRepairReport:
    decision_kind: IdempotencyRepairDecisionKind
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
    component_digests: tuple[bytes, ...]
    previous_attempt_number: int
    resolved_attempt_number: int
    carried_dead_letter_digest: bytes
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


def assess_idempotency_repair(*, repair_plan: IdempotencyRepairPlan | None, terminal_receipt_report: Any, finality_report: Any, prune_guard_report: Any, retry_escrow_report: Any | None = None, dead_letter_report: Any | None = None) -> IdempotencyRepairReport:
    action = SideEffectAction(getattr(terminal_receipt_report, "action"))
    profile_id = getattr(terminal_receipt_report, "profile_id")
    service_name = getattr(terminal_receipt_report, "service_name")
    scope_digest = getattr(terminal_receipt_report, "scope_digest")
    request_digest = getattr(terminal_receipt_report, "request_digest")
    payload_digest = getattr(terminal_receipt_report, "payload_digest")
    idempotency_key = getattr(terminal_receipt_report, "idempotency_key")
    component_digests = (_digest(terminal_receipt_report), _digest(finality_report), _digest(prune_guard_report), _digest(retry_escrow_report), _digest(dead_letter_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    for label, report in (("terminal receipt", terminal_receipt_report), ("finality", finality_report), ("prune guard", prune_guard_report)):
        if not _accept(report) or _quarantined(report):
            return _report(IdempotencyRepairDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, f"{label} did not accept", **common)
    if _watch(terminal_receipt_report) or _watch(finality_report):
        return _report(IdempotencyRepairDecisionKind.HOLD_TERMINAL_WATCH, False, True, "terminal receipt/finality still watchful", **common)
    if repair_plan is None:
        return _report(IdempotencyRepairDecisionKind.HOLD_MISSING_PLAN, False, True, "missing idempotency repair plan", **common)
    for report in (finality_report, prune_guard_report, retry_escrow_report, dead_letter_report):
        if report is None:
            continue
        for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
            if getattr(report, attr) != expected:
                return _report(IdempotencyRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"{attr} drift", plan_digest=repair_plan.plan_digest, **common)
    for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(repair_plan, attr) != expected:
            return _report(IdempotencyRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"plan {attr} drift", plan_digest=repair_plan.plan_digest, **common)
    if repair_plan.terminal_receipt_digest != component_digests[0] or repair_plan.finality_digest != component_digests[1] or repair_plan.prune_guard_digest != component_digests[2] or repair_plan.retry_escrow_digest != component_digests[3] or repair_plan.dead_letter_digest != component_digests[4]:
        return _report(IdempotencyRepairDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "component digest drift", plan_digest=repair_plan.plan_digest, **common)
    hard = int(getattr(finality_report, "hard_negative_count", 0) or 0) + int(getattr(prune_guard_report, "hard_negative_count", 0) or 0)
    if hard:
        return _report(IdempotencyRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block idempotency repair", plan_digest=repair_plan.plan_digest, **common)
    has_retry_lineage = retry_escrow_report is not None or dead_letter_report is not None or repair_plan.retry_escrow_digest != ZERO_DIGEST or repair_plan.dead_letter_digest != ZERO_DIGEST
    if has_retry_lineage:
        if repair_plan.resolved_attempt_number <= repair_plan.previous_attempt_number:
            return _report(IdempotencyRepairDecisionKind.QUARANTINE_ATTEMPT_REGRESSION, False, False, "resolved attempt did not advance", plan_digest=repair_plan.plan_digest, previous_attempt_number=repair_plan.previous_attempt_number, resolved_attempt_number=repair_plan.resolved_attempt_number, carried_dead_letter_digest=repair_plan.carried_dead_letter_digest, **common)
        if repair_plan.carried_dead_letter_digest == ZERO_DIGEST or repair_plan.carried_dead_letter_digest != component_digests[4]:
            return _report(IdempotencyRepairDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_CARRY, False, False, "retry repair did not carry dead-letter digest", plan_digest=repair_plan.plan_digest, previous_attempt_number=repair_plan.previous_attempt_number, resolved_attempt_number=repair_plan.resolved_attempt_number, carried_dead_letter_digest=repair_plan.carried_dead_letter_digest, **common)
        return _report(IdempotencyRepairDecisionKind.ACCEPT_RETRY_LINEAGE_REPAIR, True, False, "idempotency repair carried retry/dead-letter lineage", plan_digest=repair_plan.plan_digest, previous_attempt_number=repair_plan.previous_attempt_number, resolved_attempt_number=repair_plan.resolved_attempt_number, carried_dead_letter_digest=repair_plan.carried_dead_letter_digest, **common)
    if repair_plan.previous_attempt_number != 0 or repair_plan.resolved_attempt_number != 0 or repair_plan.carried_dead_letter_digest != ZERO_DIGEST:
        return _report(IdempotencyRepairDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "terminal no-retry repair carried retry fields", plan_digest=repair_plan.plan_digest, previous_attempt_number=repair_plan.previous_attempt_number, resolved_attempt_number=repair_plan.resolved_attempt_number, carried_dead_letter_digest=repair_plan.carried_dead_letter_digest, **common)
    return _report(IdempotencyRepairDecisionKind.ACCEPT_TERMINAL_REPAIR, True, False, "terminal idempotency repair accepted", plan_digest=repair_plan.plan_digest, previous_attempt_number=0, resolved_attempt_number=0, carried_dead_letter_digest=ZERO_DIGEST, **common)


def _report(kind: IdempotencyRepairDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], plan_digest: bytes = ZERO_DIGEST, previous_attempt_number: int = 0, resolved_attempt_number: int = 0, carried_dead_letter_digest: bytes = ZERO_DIGEST) -> IdempotencyRepairReport:
    digest = sha256(IDEMPOTENCY_REPAIR_DOMAIN + b":report:" + bencode({
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
        b"components": component_digests,
        b"prev_attempt": previous_attempt_number,
        b"resolved_attempt": resolved_attempt_number,
        b"carried_dead": carried_dead_letter_digest,
    }))
    return IdempotencyRepairReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, plan_digest, component_digests, previous_attempt_number, resolved_attempt_number, carried_dead_letter_digest, digest)
