"""Recovery mesh after effect seal and seal replay.

rev0056 joins effect-seal, seal-replay, restart-chaos, and corpus-witness
reports before post-restart state can become clean/sticky.  The recovery mesh is
not a live side-effect runner.  It decides whether the local node may regard an
effect as recovered, hold watch debt, repair an ambiguity, or quarantine drift.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction, SideEffectPhase

RECOVERY_MESH_DOMAIN = DOMAIN + b":recovery-mesh-v1:"


class RecoveryMeshDecisionKind(str, Enum):
    ACCEPT_RECOVERED_COMMITTED = "accept_recovered_committed"
    ACCEPT_RECOVERED_ABORTED = "accept_recovered_aborted"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_REPAIR_REQUIRED = "hold_repair_required"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_COMPONENT_DRIFT = "quarantine_component_drift"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_PHASE_DRIFT = "quarantine_phase_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RecoveryMeshReport:
    decision_kind: RecoveryMeshDecisionKind
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
    repair_required: bool
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


def assess_recovery_mesh(
    *,
    effect_seal_report: Any,
    seal_replay_report: Any,
    restart_chaos_report: Any,
    corpus_witness_report: Any,
    require_corpus_witness: bool = True,
    allow_watch: bool = False,
) -> RecoveryMeshReport:
    action = SideEffectAction(getattr(effect_seal_report, "action"))
    phase = getattr(effect_seal_report, "final_phase", None)
    final_phase = SideEffectPhase(phase) if phase is not None else None
    profile_id = getattr(effect_seal_report, "profile_id")
    service_name = getattr(effect_seal_report, "service_name")
    scope_digest = getattr(effect_seal_report, "scope_digest")
    request_digest = getattr(effect_seal_report, "request_digest")
    payload_digest = getattr(effect_seal_report, "payload_digest")
    idempotency_key = getattr(effect_seal_report, "idempotency_key")
    components = (effect_seal_report, seal_replay_report, restart_chaos_report, corpus_witness_report)
    component_digests = tuple(_digest(component) for component in components)
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    for component in components:
        if require_corpus_witness or component is not corpus_witness_report:
            if not _accept(component) or _quarantined(component):
                return _report(RecoveryMeshDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component did not accept", repair_required=False, **common)
    for component in (seal_replay_report, restart_chaos_report):
        if getattr(component, "profile_id", profile_id) != profile_id or getattr(component, "service_name", service_name) != service_name:
            return _report(RecoveryMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "profile/service boundary drift", repair_required=False, **common)
        if getattr(component, "scope_digest", scope_digest) != scope_digest or getattr(component, "request_digest", request_digest) != request_digest:
            return _report(RecoveryMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request boundary drift", repair_required=False, **common)
        if getattr(component, "payload_digest", payload_digest) != payload_digest:
            return _report(RecoveryMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "payload boundary drift", repair_required=False, **common)
        if getattr(component, "idempotency_key", idempotency_key) != idempotency_key:
            return _report(RecoveryMeshDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "idempotency boundary drift", repair_required=False, **common)
    for component in (seal_replay_report, restart_chaos_report):
        cphase = getattr(component, "final_phase", None)
        if cphase is not None and final_phase is not None and SideEffectPhase(cphase) is not final_phase:
            return _report(RecoveryMeshDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "phase drift", repair_required=False, **common)
    hard = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components)
    if hard:
        return _report(RecoveryMeshDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block recovery", repair_required=False, hard_negative_count=hard, **common)
    if require_corpus_witness and not corpus_witness_report.receipt_digests:
        return _report(RecoveryMeshDecisionKind.HOLD_REPAIR_REQUIRED, False, True, "corpus witness missing receipts", repair_required=True, **common)
    if any(_watch(component) for component in components):
        if not allow_watch:
            return _report(RecoveryMeshDecisionKind.HOLD_COMPONENT_WATCH, False, True, "watch pressure carried into recovery", repair_required=False, **common)
        return _report(RecoveryMeshDecisionKind.ACCEPT_WITH_WATCH, True, True, "recovery mesh accepted with watch", repair_required=False, **common)
    if final_phase is SideEffectPhase.ABORT:
        return _report(RecoveryMeshDecisionKind.ACCEPT_RECOVERED_ABORTED, True, False, "recovered aborted effect", repair_required=False, **common)
    return _report(RecoveryMeshDecisionKind.ACCEPT_RECOVERED_COMMITTED, True, False, "recovered committed effect", repair_required=False, **common)


def _report(kind: RecoveryMeshDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], repair_required: bool, hard_negative_count: int = 0) -> RecoveryMeshReport:
    digest = sha256(RECOVERY_MESH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"phase": final_phase.value if final_phase else b"none",
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"components": list(component_digests),
        b"hard": hard_negative_count,
        b"repair": 1 if repair_required else 0,
    }))
    return RecoveryMeshReport(kind, accept, watch, reason, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, component_digests, hard_negative_count, repair_required, digest)
