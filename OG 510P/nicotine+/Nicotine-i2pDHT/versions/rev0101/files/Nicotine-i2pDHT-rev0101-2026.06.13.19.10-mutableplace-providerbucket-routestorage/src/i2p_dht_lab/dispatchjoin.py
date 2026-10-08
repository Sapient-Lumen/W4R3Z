"""Join cross-surface binding with outbound egress before handler dispatch.

By rev0028 the cube had separate safety surfaces: validator walls, capability
checks, misbind guards, scheduling, and egress-ish probe budgets.  The dangerous
bug class is a joined boundary: a handler sees one accepted report and forgets
that outbound work may belong to a different scope, request, actor, or metadata
budget.

This module keeps the final toy handler gate small: a bound intent must still
pass misbind pressure and the egress window attached to that exact intent.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .egressmeter import EgressBudget, EgressEvent, EgressEventKind, EgressWindowReport, assess_egress_window
from .ids import DOMAIN, sha256
from .misbindguard import HandlerIntent, HandlerIntentKind, MisbindGuardReport

DISPATCH_JOIN_DOMAIN = DOMAIN + b":dispatch-join-v1:"


class DispatchJoinDecisionKind(str, Enum):
    ACCEPT_BOUND_DISPATCH = "accept_bound_dispatch"
    ACCEPT_WITH_EGRESS_WATCH = "accept_with_egress_watch"
    REJECT_MISBIND_GUARD = "reject_misbind_guard"
    REJECT_EGRESS_BUDGET = "reject_egress_budget"
    REJECT_FORBIDDEN_RAW_KEY_EGRESS = "reject_forbidden_raw_key_egress"
    REJECT_MISSING_REQUIRED_EGRESS = "reject_missing_required_egress"
    QUARANTINE_SCOPE_LEAK = "quarantine_scope_leak"
    QUARANTINE_OBJECT_LEAK = "quarantine_object_leak"


REQUIRED_EGRESS_BY_INTENT: dict[HandlerIntentKind, frozenset[EgressEventKind]] = {
    HandlerIntentKind.MUTABLE_HEAD_WRITE: frozenset({EgressEventKind.WITNESS_PUBLISH, EgressEventKind.SAM_STREAM_SEND}),
    HandlerIntentKind.STORE_RECORD: frozenset({EgressEventKind.STORE_REQUEST, EgressEventKind.SAM_STREAM_SEND}),
    HandlerIntentKind.PROVIDER_PUBLISH: frozenset({EgressEventKind.PROVIDER_REAL_PROBE, EgressEventKind.PROVIDER_DECOY_PROBE}),
    HandlerIntentKind.WITNESS_ACCEPT: frozenset({EgressEventKind.WITNESS_PUBLISH}),
    HandlerIntentKind.REPAIR_OFFER_ACCEPT: frozenset({EgressEventKind.REPAIR_REQUEST, EgressEventKind.USEFUL_REFUSAL}),
    HandlerIntentKind.USEFUL_REFUSAL_RECORD: frozenset({EgressEventKind.USEFUL_REFUSAL}),
}

RAW_FORBIDDEN_INTENTS = frozenset({
    HandlerIntentKind.WITNESS_ACCEPT,
    HandlerIntentKind.USEFUL_REFUSAL_RECORD,
    HandlerIntentKind.REPAIR_OFFER_ACCEPT,
})


@dataclass(frozen=True)
class DispatchJoinReport:
    decision_kind: DispatchJoinDecisionKind
    accept: bool
    reason: str
    misbind_digest: bytes
    egress_digest: bytes
    leaked_event_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: DispatchJoinDecisionKind, accept: bool, reason: str, *, intent: HandlerIntent, misbind: MisbindGuardReport, egress: EgressWindowReport, leaked: Iterable[bytes] = ()) -> DispatchJoinReport:
    leaked_tuple = tuple(sorted(leaked))
    digest = sha256(DISPATCH_JOIN_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"intent": intent.kind.value,
        b"misbind": misbind.report_digest,
        b"egress": egress.report_digest,
        b"leaked": leaked_tuple,
    }))
    return DispatchJoinReport(kind, accept, reason, misbind.report_digest, egress.report_digest, leaked_tuple, digest)


def assess_bound_dispatch(
    *,
    intent: HandlerIntent,
    misbind: MisbindGuardReport,
    egress_events: Iterable[EgressEvent],
    now: int,
    budget: EgressBudget | None = None,
) -> DispatchJoinReport:
    event_tuple = tuple(egress_events)
    egress = assess_egress_window(event_tuple, budget=budget, now=now)
    if not misbind.accept:
        return _report(DispatchJoinDecisionKind.REJECT_MISBIND_GUARD, False, "handler intent failed the cross-surface misbind guard", intent=intent, misbind=misbind, egress=egress)
    if not egress.accept:
        kind = DispatchJoinDecisionKind.REJECT_EGRESS_BUDGET
        if egress.quarantined:
            reason = "egress budget produced quarantine pressure before handler dispatch"
        else:
            reason = "egress budget rejected outbound work before handler dispatch"
        return _report(kind, False, reason, intent=intent, misbind=misbind, egress=egress)
    scope_leaks = tuple(event.event_digest for event in event_tuple if event.scope_id != intent.scope_id)
    if scope_leaks:
        return _report(DispatchJoinDecisionKind.QUARANTINE_SCOPE_LEAK, False, "egress event scope does not match bound handler intent", intent=intent, misbind=misbind, egress=egress, leaked=scope_leaks)
    object_leaks = tuple(event.event_digest for event in event_tuple if event.object_digest != intent.body_digest)
    if object_leaks:
        return _report(DispatchJoinDecisionKind.QUARANTINE_OBJECT_LEAK, False, "egress event object digest does not match bound handler body digest", intent=intent, misbind=misbind, egress=egress, leaked=object_leaks)
    if intent.kind in RAW_FORBIDDEN_INTENTS and any(event.exposes_raw_key for event in event_tuple):
        return _report(DispatchJoinDecisionKind.REJECT_FORBIDDEN_RAW_KEY_EGRESS, False, "handler intent forbids raw-key egress even when budget permits it", intent=intent, misbind=misbind, egress=egress)
    required = REQUIRED_EGRESS_BY_INTENT[intent.kind]
    if event_tuple and not any(event.kind in required for event in event_tuple):
        return _report(DispatchJoinDecisionKind.REJECT_MISSING_REQUIRED_EGRESS, False, "egress window lacks an event kind required by this handler intent", intent=intent, misbind=misbind, egress=egress)
    if egress.decision_kind.value.endswith("watch") or egress.decision_kind.value == "accept_with_watch":
        return _report(DispatchJoinDecisionKind.ACCEPT_WITH_EGRESS_WATCH, True, "bound dispatch accepted with egress watch pressure", intent=intent, misbind=misbind, egress=egress)
    return _report(DispatchJoinDecisionKind.ACCEPT_BOUND_DISPATCH, True, "bound dispatch passed misbind and egress pressure", intent=intent, misbind=misbind, egress=egress)
