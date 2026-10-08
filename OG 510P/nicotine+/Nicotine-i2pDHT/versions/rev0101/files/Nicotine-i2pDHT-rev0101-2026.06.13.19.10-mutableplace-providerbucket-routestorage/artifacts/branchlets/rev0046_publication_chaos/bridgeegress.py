"""Public bridge egress gate after shadow-fire.

rev0045 made public bridge side effects shadow-fireable without letting them
reach live transport. rev0046 adds the next boundary: even a locally accepted
shadow-fire report cannot spend outbound bandwidth until its egress window is
fresh, exact-scope, non-replayed, and metadata-budgeted.

This is still no-network toy code. It exists to keep future SAM/I2P work from
turning a valid control-plane decision into an unbounded public bridge send.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .egressmeter import EgressDecisionKind, EgressEvent, EgressEventKind, EgressWindowReport
from .ids import DOMAIN, sha256
from .shadowfire import ShadowFireAction, ShadowFireDecisionKind, ShadowFireReport

BRIDGE_EGRESS_DOMAIN = DOMAIN + b":bridge-egress-v1:"


class BridgeEgressDecisionKind(str, Enum):
    ACCEPT_BRIDGE_EGRESS = "accept_bridge_egress"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_SHADOW_WATCH = "hold_shadow_watch"
    HOLD_EGRESS_WATCH = "hold_egress_watch"
    HOLD_SHADOW_NOT_ACCEPTED = "hold_shadow_not_accepted"
    REJECT_EGRESS_NOT_ACCEPTED = "reject_egress_not_accepted"
    REJECT_RAW_KEY_EGRESS = "reject_raw_key_egress"
    QUARANTINE_SHADOW_REJECTED = "quarantine_shadow_rejected"
    QUARANTINE_ACTION_MISMATCH = "quarantine_action_mismatch"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_OBJECT_DRIFT = "quarantine_request_object_drift"
    QUARANTINE_EVENT_REPLAY = "quarantine_event_replay"
    QUARANTINE_DESTINATION_MONOCULTURE = "quarantine_destination_monoculture"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"


REQUIRED_EVENT_KINDS: dict[ShadowFireAction, frozenset[EgressEventKind]] = {
    ShadowFireAction.PUBLIC_BRIDGE_REFRESH: frozenset({EgressEventKind.SAM_STREAM_SEND, EgressEventKind.ROUTE_GOSSIP, EgressEventKind.WITNESS_PUBLISH}),
    ShadowFireAction.PUBLIC_BRIDGE_WITHDRAW: frozenset({EgressEventKind.SAM_STREAM_SEND, EgressEventKind.WITNESS_PUBLISH, EgressEventKind.USEFUL_REFUSAL}),
    ShadowFireAction.PUBLIC_BRIDGE_REPAIR: frozenset({EgressEventKind.SAM_STREAM_SEND, EgressEventKind.REPAIR_REQUEST, EgressEventKind.WITNESS_PUBLISH}),
}


@dataclass(frozen=True)
class BridgeEgressPlan:
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    object_digest: bytes
    required_destination_families: int = 2
    allow_watch: bool = False
    allow_raw_key_egress: bool = False

    def __post_init__(self) -> None:
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("object_digest", self.object_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.required_destination_families < 1:
            raise ValueError("required_destination_families must be positive")
        object.__setattr__(self, "action", ShadowFireAction(self.action))


@dataclass(frozen=True)
class BridgeEgressReport:
    decision_kind: BridgeEgressDecisionKind
    accepted: bool
    reason: str
    action: ShadowFireAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    object_digest: bytes
    shadow_digest: bytes
    egress_report_digest: bytes
    event_digests: tuple[bytes, ...]
    destination_families: tuple[str, ...]
    watch: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: BridgeEgressDecisionKind, accepted: bool, reason: str, *, plan: BridgeEgressPlan, shadow_fire: ShadowFireReport, egress: EgressWindowReport, events: Iterable[EgressEvent] = (), watch: bool = False) -> BridgeEgressReport:
    event_tuple = tuple(events)
    event_digests = tuple(sorted(event.event_digest for event in event_tuple))
    families = tuple(sorted({event.destination_family for event in event_tuple} or set(egress.destination_families)))
    digest = sha256(BRIDGE_EGRESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"action": plan.action.value,
        b"profile": plan.profile_id,
        b"service": plan.service_name,
        b"scope": plan.scope_digest,
        b"request": plan.request_digest,
        b"object": plan.object_digest,
        b"shadow": shadow_fire.report_digest,
        b"egress": egress.report_digest,
        b"events": list(event_digests),
        b"families": list(families),
        b"watch": 1 if watch else 0,
    }))
    return BridgeEgressReport(kind, accepted, reason, plan.action, plan.profile_id, plan.service_name, plan.scope_digest, plan.request_digest, plan.object_digest, shadow_fire.report_digest, egress.report_digest, event_digests, families, watch, digest)


def assess_bridge_egress(*, plan: BridgeEgressPlan, shadow_fire: ShadowFireReport, egress: EgressWindowReport, events: Iterable[EgressEvent], previously_seen_event_digests: Iterable[bytes] = (), hard_negative_digests: Iterable[bytes] = ()) -> BridgeEgressReport:
    """Join shadow-fire and metered outbound events before public bridge egress.

    The egress report does not carry enough information by itself to prove the
    events are bound to the same scope/object; callers must pass the events used
    to create the window so this join can re-check exact boundaries.
    """
    event_tuple = tuple(events)
    seen = set(previously_seen_event_digests)
    if hard_negative_digests:
        return _report(BridgeEgressDecisionKind.QUARANTINE_HARD_NEGATIVE, False, "hard negative before bridge egress", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if shadow_fire.quarantined or shadow_fire.decision_kind is ShadowFireDecisionKind.QUARANTINE_COMPONENT_REJECTED:
        return _report(BridgeEgressDecisionKind.QUARANTINE_SHADOW_REJECTED, False, "shadow-fire report is quarantined", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if not shadow_fire.accepted:
        return _report(BridgeEgressDecisionKind.HOLD_SHADOW_NOT_ACCEPTED, False, "shadow-fire did not accept side effect", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if shadow_fire.watch and not plan.allow_watch:
        return _report(BridgeEgressDecisionKind.HOLD_SHADOW_WATCH, False, "shadow-fire accepted only with watch", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple, watch=True)
    if shadow_fire.action is not plan.action:
        return _report(BridgeEgressDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "shadow-fire action differs from egress plan", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if shadow_fire.profile_id != plan.profile_id or shadow_fire.service_name != plan.service_name:
        return _report(BridgeEgressDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "profile/service mismatch across shadow-fire and egress plan", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if shadow_fire.scope_digest != plan.scope_digest:
        return _report(BridgeEgressDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "scope drift across shadow-fire and egress plan", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if shadow_fire.request_digest != plan.request_digest:
        return _report(BridgeEgressDecisionKind.QUARANTINE_REQUEST_OBJECT_DRIFT, False, "request drift across shadow-fire and egress plan", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if not egress.accept:
        return _report(BridgeEgressDecisionKind.REJECT_EGRESS_NOT_ACCEPTED, False, "egress meter rejected outbound window", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if egress.decision_kind is EgressDecisionKind.ACCEPT_WITH_WATCH and not plan.allow_watch:
        return _report(BridgeEgressDecisionKind.HOLD_EGRESS_WATCH, False, "egress was accepted only with watch", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple, watch=True)
    if egress.raw_key_exposures and not plan.allow_raw_key_egress:
        return _report(BridgeEgressDecisionKind.REJECT_RAW_KEY_EGRESS, False, "public bridge egress may not spend raw-key exposure", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if any(event.event_digest in seen for event in event_tuple):
        return _report(BridgeEgressDecisionKind.QUARANTINE_EVENT_REPLAY, False, "event digest replay before public bridge egress", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    allowed = REQUIRED_EVENT_KINDS[plan.action]
    if not event_tuple or any(event.kind not in allowed for event in event_tuple):
        return _report(BridgeEgressDecisionKind.QUARANTINE_ACTION_MISMATCH, False, "egress event kind is not valid for bridge action", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    for event in event_tuple:
        if event.scope_id != plan.scope_digest:
            return _report(BridgeEgressDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "egress event scope drift", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
        if event.object_digest not in {plan.object_digest, plan.request_digest}:
            return _report(BridgeEgressDecisionKind.QUARANTINE_REQUEST_OBJECT_DRIFT, False, "egress event object/request drift", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    if len({event.destination_family for event in event_tuple}) < plan.required_destination_families:
        return _report(BridgeEgressDecisionKind.QUARANTINE_DESTINATION_MONOCULTURE, False, "bridge egress lacks destination-family diversity", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple)
    watch = bool(shadow_fire.watch or egress.decision_kind is EgressDecisionKind.ACCEPT_WITH_WATCH)
    return _report(BridgeEgressDecisionKind.ACCEPT_WITH_WATCH if watch else BridgeEgressDecisionKind.ACCEPT_BRIDGE_EGRESS, True, "shadow-fire and egress window bind to same public bridge boundary", plan=plan, shadow_fire=shadow_fire, egress=egress, events=event_tuple, watch=watch)
