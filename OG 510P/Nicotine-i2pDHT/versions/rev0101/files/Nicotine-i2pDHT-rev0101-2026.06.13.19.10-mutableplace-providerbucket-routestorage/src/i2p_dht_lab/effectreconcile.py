"""Effect reconciliation after recovery, dead-letter, and retry quorum.

rev0057 adds a local no-network reconciliation seam: prepared-only effects,
ambiguous commit/abort memory, retry votes, and hard negatives must bind to one
exact side-effect boundary before the node decides to retry, keep dead-letter,
accept a terminal effect, or quarantine drift.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .deadletter import DeadLetterKind
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .retryquorum import RetryQuorumDecisionKind
from .sideeffectjournal import SideEffectAction, SideEffectPhase

EFFECT_RECONCILE_DOMAIN = DOMAIN + b":effect-reconcile-v1:"


class EffectReconcileDecisionKind(str, Enum):
    ACCEPT_RECONCILED_COMMIT = "accept_reconciled_commit"
    ACCEPT_RECONCILED_ABORT = "accept_reconciled_abort"
    ACCEPT_RETRY = "accept_retry"
    ACCEPT_KEEP_DEAD_LETTER = "accept_keep_dead_letter"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_MISSING_RETRY = "hold_missing_retry"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_PHASE_CONFLICT = "quarantine_phase_conflict"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"


@dataclass(frozen=True)
class EffectReconcileReport:
    decision_kind: EffectReconcileDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    component_digests: tuple[bytes, ...]
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
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component report lacks report_digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def assess_effect_reconcile(
    *,
    effect_seal_report: Any,
    recovery_mesh_report: Any,
    dead_letter_report: Any,
    retry_quorum_report: Any | None = None,
    side_effect_journal_report: Any | None = None,
    allow_dead_letter_hold: bool = True,
    allow_retry: bool = True,
) -> EffectReconcileReport:
    action = SideEffectAction(getattr(effect_seal_report, "action"))
    final_raw = getattr(effect_seal_report, "final_phase", None)
    final_phase = SideEffectPhase(final_raw) if final_raw is not None else None
    profile_id = getattr(effect_seal_report, "profile_id")
    service_name = getattr(effect_seal_report, "service_name")
    scope_digest = getattr(effect_seal_report, "scope_digest")
    request_digest = getattr(effect_seal_report, "request_digest")
    payload_digest = getattr(effect_seal_report, "payload_digest")
    idempotency_key = getattr(effect_seal_report, "idempotency_key")
    components = (effect_seal_report, recovery_mesh_report, dead_letter_report, retry_quorum_report, side_effect_journal_report)
    component_digests = tuple(_digest(component) for component in components)
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    for component in (effect_seal_report, recovery_mesh_report, dead_letter_report):
        if not _accept(component) or _quarantined(component):
            return _report(EffectReconcileDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "required component did not accept", retry_required=False, dead_letter_required=True, **common)
    for component in (recovery_mesh_report, dead_letter_report, retry_quorum_report, side_effect_journal_report):
        if component is None:
            continue
        if getattr(component, "profile_id", profile_id) != profile_id or getattr(component, "service_name", service_name) != service_name:
            return _report(EffectReconcileDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "profile/service drift", retry_required=False, dead_letter_required=True, **common)
        if getattr(component, "scope_digest", scope_digest) != scope_digest or getattr(component, "request_digest", request_digest) != request_digest:
            return _report(EffectReconcileDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request drift", retry_required=False, dead_letter_required=True, **common)
        if getattr(component, "payload_digest", payload_digest) != payload_digest or getattr(component, "idempotency_key", idempotency_key) != idempotency_key:
            return _report(EffectReconcileDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "payload/idempotency drift", retry_required=False, dead_letter_required=True, **common)
    hard = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)
    if hard:
        return _report(EffectReconcileDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block reconcile", retry_required=False, dead_letter_required=True, hard_negative_count=hard, **common)
    dead_kinds = set(getattr(dead_letter_report, "kinds", ()))
    dead_kind_values = {DeadLetterKind(kind) for kind in dead_kinds}
    dead_phase = getattr(dead_letter_report, "observed_phase", None)
    if dead_phase is not None and final_phase is not None and SideEffectPhase(dead_phase) is not final_phase:
        return _report(EffectReconcileDecisionKind.QUARANTINE_PHASE_CONFLICT, False, False, "dead-letter phase conflicts with effect seal", retry_required=False, dead_letter_required=True, **common)
    if side_effect_journal_report is not None:
        journal_phase = getattr(side_effect_journal_report, "final_phase", None)
        if journal_phase is not None and final_phase is not None and SideEffectPhase(journal_phase) is not final_phase:
            return _report(EffectReconcileDecisionKind.QUARANTINE_PHASE_CONFLICT, False, False, "journal phase conflicts with effect seal", retry_required=False, dead_letter_required=True, **common)
    if any(_watch(component) for component in (effect_seal_report, recovery_mesh_report, dead_letter_report)):
        if retry_quorum_report is None:
            return _report(EffectReconcileDecisionKind.HOLD_COMPONENT_WATCH, False, True, "watch pressure needs retry quorum or dead-letter hold", retry_required=True, dead_letter_required=True, **common)
    if final_phase is SideEffectPhase.COMMIT and DeadLetterKind.AMBIGUOUS_ABORT in dead_kind_values:
        return _report(EffectReconcileDecisionKind.QUARANTINE_PHASE_CONFLICT, False, False, "commit conflicts with ambiguous abort", retry_required=False, dead_letter_required=True, **common)
    if final_phase is SideEffectPhase.ABORT and DeadLetterKind.AMBIGUOUS_COMMIT in dead_kind_values:
        return _report(EffectReconcileDecisionKind.QUARANTINE_PHASE_CONFLICT, False, False, "abort conflicts with ambiguous commit", retry_required=False, dead_letter_required=True, **common)
    if retry_quorum_report is not None:
        if _quarantined(retry_quorum_report):
            return _report(EffectReconcileDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "retry quorum quarantined", retry_required=True, dead_letter_required=True, **common)
        if _accept(retry_quorum_report) and getattr(retry_quorum_report, "decision_kind", None) == RetryQuorumDecisionKind.ACCEPT_RETRY_QUORUM:
            if allow_retry:
                return _report(EffectReconcileDecisionKind.ACCEPT_RETRY, True, True, "retry accepted without erasing dead-letter", retry_required=True, dead_letter_required=True, **common)
        if _accept(retry_quorum_report) and getattr(retry_quorum_report, "decision_kind", None) == RetryQuorumDecisionKind.ACCEPT_REFUSAL_BACKOFF:
            return _report(EffectReconcileDecisionKind.ACCEPT_KEEP_DEAD_LETTER, True, True, "useful refusal backoff keeps dead-letter", retry_required=True, dead_letter_required=True, **common)
    if final_phase is SideEffectPhase.COMMIT:
        return _report(EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT, True, False, "commit reconciled", retry_required=False, dead_letter_required=False, **common)
    if final_phase is SideEffectPhase.ABORT:
        return _report(EffectReconcileDecisionKind.ACCEPT_RECONCILED_ABORT, True, False, "abort reconciled", retry_required=False, dead_letter_required=False, **common)
    if allow_dead_letter_hold:
        return _report(EffectReconcileDecisionKind.ACCEPT_KEEP_DEAD_LETTER, True, True, "prepared-only or unresolved effect remains dead-lettered", retry_required=True, dead_letter_required=True, **common)
    return _report(EffectReconcileDecisionKind.HOLD_MISSING_RETRY, False, True, "missing retry quorum for unresolved effect", retry_required=True, dead_letter_required=True, **common)


def _report(kind: EffectReconcileDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], retry_required: bool, dead_letter_required: bool, hard_negative_count: int = 0) -> EffectReconcileReport:
    digest = sha256(EFFECT_RECONCILE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"phase": b"" if final_phase is None else final_phase.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"components": list(component_digests),
        b"hard": hard_negative_count,
        b"retry": 1 if retry_required else 0,
        b"dead": 1 if dead_letter_required else 0,
    }))
    return EffectReconcileReport(kind, accept, watch, reason, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, component_digests, hard_negative_count, retry_required, dead_letter_required, digest)
