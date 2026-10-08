"""Joined service exit/resume gate.

rev0040 joins operator intent, circuit-breaker pressure, drain reports, and
continuity memory before a garden service can pause, demote, disable bridge
mode, freeze, or resume.  A valid operator capsule alone is not enough; a
tripped breaker alone is not enough; a successful drain alone is not enough.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .operatorintent import OperatorIntentAction, OperatorIntentReport
from .servicebreaker import ServiceBreakerReport, ServiceBreakerState
from .servicedrain import ServiceDrainReport

SERVICE_EXIT_DOMAIN = DOMAIN + b":service-exit-v1:"


class ServiceExitSignalKind(str, Enum):
    OPERATOR_INTENT = "operator_intent"
    BREAKER = "breaker"
    DRAIN = "drain"
    CONTINUITY_JOURNAL = "continuity_journal"
    PROFILE_GC = "profile_gc"


class ServiceExitDecisionKind(str, Enum):
    ACCEPT_PAUSE = "accept_pause"
    ACCEPT_DEMOTE_TO_LEAF = "accept_demote_to_leaf"
    ACCEPT_DISABLE_BRIDGE = "accept_disable_bridge"
    ACCEPT_RESUME = "accept_resume"
    ACCEPT_EMERGENCY_FREEZE = "accept_emergency_freeze"
    HOLD_NEEDS_OPERATOR_INTENT = "hold_needs_operator_intent"
    HOLD_NEEDS_BREAKER_OR_DRAIN = "hold_needs_breaker_or_drain"
    HOLD_NEEDS_CLEAN_DRAIN = "hold_needs_clean_drain"
    HOLD_RESUME_NEEDS_CLOSED_BREAKER = "hold_resume_needs_closed_breaker"
    QUARANTINE_SIGNAL = "quarantine_signal"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_ACTION_MISMATCH = "quarantine_action_mismatch"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"


@dataclass(frozen=True)
class ServiceExitSignal:
    kind: ServiceExitSignalKind
    report_digest: bytes
    accept: bool
    quarantined: bool
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    action: OperatorIntentAction | None = None
    breaker_state: ServiceBreakerState | None = None
    hard_negative_preserved: bool = True
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        for name, value in (("report_digest", self.report_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"report": self.report_digest,
            b"accept": 1 if self.accept else 0,
            b"quarantined": 1 if self.quarantined else 0,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"action": self.action.value if self.action else "",
            b"breaker_state": self.breaker_state.value if self.breaker_state else "",
            b"hard_negative_preserved": 1 if self.hard_negative_preserved else 0,
            b"detail": self.detail,
        }


@dataclass(frozen=True)
class ServiceExitPolicy:
    require_clean_drain_for_demote: bool = True
    require_clean_drain_for_bridge_disable: bool = True
    require_continuity_memory_for_exit: bool = True
    require_profile_gc_for_demote: bool = True


@dataclass(frozen=True)
class ServiceExitReport:
    decision_kind: ServiceExitDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    request_digest: bytes | None
    action: OperatorIntentAction | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def signal_from_operator_intent(report: OperatorIntentReport) -> ServiceExitSignal:
    return ServiceExitSignal(
        kind=ServiceExitSignalKind.OPERATOR_INTENT,
        report_digest=report.report_digest,
        accept=report.accept,
        quarantined=report.quarantined,
        service_name=report.service_name or "unknown",
        scope_digest=report.scope_digest or b"\x00" * 32,
        request_digest=report.request_digest or b"\x00" * 32,
        action=report.action,
        detail=report.decision_kind.value,
    )


def signal_from_breaker(report: ServiceBreakerReport, *, request_digest: bytes) -> ServiceExitSignal:
    return ServiceExitSignal(
        kind=ServiceExitSignalKind.BREAKER,
        report_digest=report.report_digest,
        accept=report.accept,
        quarantined=report.quarantined,
        service_name=report.service_name or "unknown",
        scope_digest=report.scope_digest or b"\x00" * 32,
        request_digest=request_digest,
        breaker_state=report.state,
        detail=report.decision_kind.value,
    )


def signal_from_drain(report: ServiceDrainReport, *, request_digest: bytes) -> ServiceExitSignal:
    return ServiceExitSignal(
        kind=ServiceExitSignalKind.DRAIN,
        report_digest=report.report_digest,
        accept=report.accept,
        quarantined=report.quarantined,
        service_name=report.service_name or "unknown",
        scope_digest=report.scope_digest or b"\x00" * 32,
        request_digest=request_digest,
        detail=report.decision_kind.value,
    )


def make_service_exit_signal(
    *,
    kind: ServiceExitSignalKind,
    report_digest: bytes,
    accept: bool,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    quarantined: bool = False,
    action: OperatorIntentAction | None = None,
    breaker_state: ServiceBreakerState | None = None,
    hard_negative_preserved: bool = True,
    detail: str = "",
) -> ServiceExitSignal:
    return ServiceExitSignal(kind, report_digest, accept, quarantined, service_name, scope_digest, request_digest, action, breaker_state, hard_negative_preserved, detail)


def _report(kind: ServiceExitDecisionKind, accept: bool, reason: str, signals: Iterable[ServiceExitSignal], action: OperatorIntentAction | None = None) -> ServiceExitReport:
    sigs = tuple(sorted(signals, key=lambda item: (item.kind.value, item.report_digest)))
    service = sigs[0].service_name if sigs else None
    scope = sigs[0].scope_digest if sigs else None
    request = sigs[0].request_digest if sigs else None
    digest = sha256(SERVICE_EXIT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": service or "",
        b"scope": scope or b"",
        b"request": request or b"",
        b"action": action.value if action else "",
        b"signals": [signal.bvalue() for signal in sigs],
    }))
    return ServiceExitReport(kind, accept, reason, service, scope, request, action, digest)


def assess_service_exit(
    signals: Iterable[ServiceExitSignal],
    *,
    policy: ServiceExitPolicy | None = None,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previously_seen_reports: Iterable[bytes] = (),
) -> ServiceExitReport:
    policy = policy or ServiceExitPolicy()
    sigs = tuple(signals)
    if not sigs:
        return _report(ServiceExitDecisionKind.HOLD_NEEDS_OPERATOR_INTENT, False, "no exit signals", sigs)
    seen = set(previously_seen_reports)
    if any(signal.report_digest in seen for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_REPLAY, False, "exit signal replayed", sigs)
    if any(signal.quarantined for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_SIGNAL, False, "exit signal was quarantined", sigs)
    if any(signal.service_name != expected_service_name for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "exit service drift", sigs)
    if any(signal.scope_digest != expected_scope_digest for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "exit scope drift", sigs)
    if any(signal.request_digest != expected_request_digest for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "exit request drift", sigs)
    if any(not signal.hard_negative_preserved for signal in sigs):
        return _report(ServiceExitDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "exit would drop hard negative memory", sigs)
    intent_signals = [s for s in sigs if s.kind is ServiceExitSignalKind.OPERATOR_INTENT]
    if not intent_signals or not intent_signals[-1].accept or intent_signals[-1].action is None:
        return _report(ServiceExitDecisionKind.HOLD_NEEDS_OPERATOR_INTENT, False, "exit needs accepted operator intent", sigs)
    action = intent_signals[-1].action
    breaker = next((s for s in sigs if s.kind is ServiceExitSignalKind.BREAKER), None)
    drain = next((s for s in sigs if s.kind is ServiceExitSignalKind.DRAIN), None)
    continuity = next((s for s in sigs if s.kind is ServiceExitSignalKind.CONTINUITY_JOURNAL), None)
    profile_gc = next((s for s in sigs if s.kind is ServiceExitSignalKind.PROFILE_GC), None)
    if policy.require_continuity_memory_for_exit and action is not OperatorIntentAction.RESUME_SERVICE and (continuity is None or not continuity.accept):
        return _report(ServiceExitDecisionKind.HOLD_NEEDS_BREAKER_OR_DRAIN, False, "exit needs continuity memory", sigs, action=action)
    if action is OperatorIntentAction.PAUSE_SERVICE:
        if breaker and breaker.breaker_state is ServiceBreakerState.OPEN:
            return _report(ServiceExitDecisionKind.ACCEPT_PAUSE, True, "operator pause joined to open breaker", sigs, action=action)
        return _report(ServiceExitDecisionKind.HOLD_NEEDS_BREAKER_OR_DRAIN, False, "pause needs breaker pressure", sigs, action=action)
    if action is OperatorIntentAction.EMERGENCY_FREEZE:
        return _report(ServiceExitDecisionKind.ACCEPT_EMERGENCY_FREEZE, True, "emergency freeze accepted as local hold", sigs, action=action)
    if action is OperatorIntentAction.DEMOTE_TO_LEAF:
        if policy.require_profile_gc_for_demote and (profile_gc is None or not profile_gc.accept):
            return _report(ServiceExitDecisionKind.HOLD_NEEDS_CLEAN_DRAIN, False, "demotion needs profile GC preservation", sigs, action=action)
        if policy.require_clean_drain_for_demote and (drain is None or not drain.accept):
            return _report(ServiceExitDecisionKind.HOLD_NEEDS_CLEAN_DRAIN, False, "demotion needs clean drain", sigs, action=action)
        return _report(ServiceExitDecisionKind.ACCEPT_DEMOTE_TO_LEAF, True, "demotion joined to clean drain and profile memory", sigs, action=action)
    if action is OperatorIntentAction.DISABLE_BRIDGE:
        if policy.require_clean_drain_for_bridge_disable and (drain is None or not drain.accept):
            return _report(ServiceExitDecisionKind.HOLD_NEEDS_CLEAN_DRAIN, False, "bridge disable needs clean drain", sigs, action=action)
        return _report(ServiceExitDecisionKind.ACCEPT_DISABLE_BRIDGE, True, "bridge disable joined to clean drain", sigs, action=action)
    if action is OperatorIntentAction.RESUME_SERVICE:
        if breaker is None or breaker.breaker_state not in {ServiceBreakerState.CLOSED, ServiceBreakerState.HALF_OPEN} or not breaker.accept:
            return _report(ServiceExitDecisionKind.HOLD_RESUME_NEEDS_CLOSED_BREAKER, False, "resume needs closed or half-open breaker", sigs, action=action)
        if drain and drain.accept:
            return _report(ServiceExitDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "resume conflicts with accepted drain", sigs, action=action)
        return _report(ServiceExitDecisionKind.ACCEPT_RESUME, True, "resume joined to breaker recovery", sigs, action=action)
    if action is OperatorIntentAction.ENTER_MAINTENANCE:
        if drain and drain.accept:
            return _report(ServiceExitDecisionKind.ACCEPT_PAUSE, True, "maintenance joined to safe drain", sigs, action=action)
        return _report(ServiceExitDecisionKind.HOLD_NEEDS_CLEAN_DRAIN, False, "maintenance needs drain", sigs, action=action)
    return _report(ServiceExitDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "unsupported exit action", sigs, action=action)
