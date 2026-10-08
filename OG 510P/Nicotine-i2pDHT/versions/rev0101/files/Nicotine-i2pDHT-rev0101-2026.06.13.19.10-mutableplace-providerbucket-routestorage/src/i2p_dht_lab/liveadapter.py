"""No-network live adapter seam.

This is the rev0052 boundary that deliberately still does not go live.  It joins
router-canary, ingress-drain, backpressure, and effect-ledger style reports into
a signed adapter plan.  The adapter plan is the last rehearsal before a future
implementation gets permission to either send an outbound public frame or drain
an inbound public request into a handler.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .backpressuremesh import BackpressureMode
from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

LIVE_ADAPTER_DOMAIN = DOMAIN + b":live-adapter-v1:"


class LiveAdapterMode(str, Enum):
    OUTBOUND_PUBLIC_SEND = "outbound_public_send"
    INBOUND_HANDLER_WORK = "inbound_handler_work"
    BIDIRECTIONAL_BRIDGE_TICK = "bidirectional_bridge_tick"


class LiveAdapterDecisionKind(str, Enum):
    ACCEPT_LIVE_ADAPTER = "accept_live_adapter"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_ROUTER_CANARY = "hold_router_canary"
    HOLD_INGRESS_DRAIN = "hold_ingress_drain"
    HOLD_BACKPRESSURE = "hold_backpressure"
    HOLD_EFFECT_LEDGER = "hold_effect_ledger"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_PLANS = "empty_no_plans"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_MODE_DRIFT = "quarantine_mode_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_FRAME_DRIFT = "quarantine_frame_drift"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_CALLER_DRIFT = "quarantine_caller_drift"
    QUARANTINE_HANDLER_DRIFT = "quarantine_handler_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_MODE_COMPONENT_MISMATCH = "quarantine_mode_component_mismatch"
    QUARANTINE_BACKPRESSURE_MODE = "quarantine_backpressure_mode"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class LiveAdapterPlan:
    mode: LiveAdapterMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    frame_digest: bytes
    session_id: str
    destination: str
    caller_digest: bytes
    handler_digest: bytes
    router_canary_digest: bytes
    ingress_drain_digest: bytes
    backpressure_digest: bytes
    effect_ledger_digest: bytes
    sequence: int
    previous_plan_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", LiveAdapterMode(self.mode))
        if not self.profile_id or not self.service_name or not self.session_id or not self.destination or not self.family_id or not self.path_family:
            raise ValueError("live adapter plan needs profile/service/session/destination/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("frame_digest", self.frame_digest),
            ("caller_digest", self.caller_digest),
            ("handler_digest", self.handler_digest),
            ("router_canary_digest", self.router_canary_digest),
            ("ingress_drain_digest", self.ingress_drain_digest),
            ("backpressure_digest", self.backpressure_digest),
            ("effect_ledger_digest", self.effect_ledger_digest),
            ("previous_plan_digest", self.previous_plan_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"mode": self.mode.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.public_payload_digest,
            b"frame": self.frame_digest,
            b"session": self.session_id,
            b"destination": self.destination,
            b"caller": self.caller_digest,
            b"handler": self.handler_digest,
            b"router": self.router_canary_digest,
            b"ingress": self.ingress_drain_digest,
            b"backpressure": self.backpressure_digest,
            b"effect": self.effect_ledger_digest,
            b"seq": self.sequence,
            b"prev": self.previous_plan_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return LIVE_ADAPTER_DOMAIN + b":plan-sig:" + bencode(self.unsigned_bvalue())

    @property
    def plan_core_digest(self) -> bytes:
        return sha256(LIVE_ADAPTER_DOMAIN + b":plan-core:" + bencode(self.unsigned_bvalue()))

    @property
    def plan_digest(self) -> bytes:
        return sha256(LIVE_ADAPTER_DOMAIN + b":plan-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class LiveAdapterReport:
    decision_kind: LiveAdapterDecisionKind
    accept: bool
    watch: bool
    reason: str
    mode: LiveAdapterMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    frame_digest: bytes
    session_id: str
    destination: str
    caller_digest: bytes
    handler_digest: bytes
    accepted_plan_digest: bytes
    plan_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _component_accept(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any | None) -> bool:
    if report is None:
        return False
    return bool(getattr(report, "quarantined", False))


def make_live_adapter_plan(
    *,
    keypair: DhtKeypair,
    mode: LiveAdapterMode,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    frame_digest: bytes,
    session_id: str,
    destination: str,
    caller_digest: bytes,
    handler_digest: bytes,
    router_canary_report: Any | None,
    ingress_drain_report: Any | None,
    backpressure_report: Any,
    effect_ledger_report: Any | None = None,
    sequence: int,
    previous_plan_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> LiveAdapterPlan:
    unsigned = LiveAdapterPlan(
        mode=mode,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        public_payload_digest=public_payload_digest,
        frame_digest=frame_digest,
        session_id=session_id,
        destination=destination,
        caller_digest=caller_digest,
        handler_digest=handler_digest,
        router_canary_digest=_component_digest(router_canary_report),
        ingress_drain_digest=_component_digest(ingress_drain_report),
        backpressure_digest=_component_digest(backpressure_report),
        effect_ledger_digest=_component_digest(effect_ledger_report),
        sequence=sequence,
        previous_plan_digest=previous_plan_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(
    kind: LiveAdapterDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    mode: LiveAdapterMode,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    frame_digest: bytes,
    session_id: str,
    destination: str,
    caller_digest: bytes,
    handler_digest: bytes,
    accepted: LiveAdapterPlan | None = None,
    plans: Iterable[LiveAdapterPlan] = (),
    components: Iterable[bytes] = (),
) -> LiveAdapterReport:
    plan_t = tuple(plans)
    plan_digests = tuple(plan.plan_digest for plan in plan_t)
    families = {plan.family_id for plan in plan_t}
    paths = {plan.path_family for plan in plan_t}
    highest = max((plan.sequence for plan in plan_t), default=-1)
    accepted_digest = accepted.plan_digest if accepted else ZERO_DIGEST
    component_t = tuple(components)
    digest = sha256(LIVE_ADAPTER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"mode": mode.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": public_payload_digest,
        b"frame": frame_digest,
        b"session": session_id,
        b"destination": destination,
        b"caller": caller_digest,
        b"handler": handler_digest,
        b"accepted": accepted_digest,
        b"plans": list(plan_digests),
        b"components": list(component_t),
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return LiveAdapterReport(kind, accept, watch, reason, mode, profile_id, service_name, scope_digest, request_digest, public_payload_digest, frame_digest, session_id, destination, caller_digest, handler_digest, accepted_digest, plan_digests, component_t, len(families), len(paths), highest, digest)


def _mode_needs_router(mode: LiveAdapterMode) -> bool:
    return mode in (LiveAdapterMode.OUTBOUND_PUBLIC_SEND, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK)


def _mode_needs_ingress(mode: LiveAdapterMode) -> bool:
    return mode in (LiveAdapterMode.INBOUND_HANDLER_WORK, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK)


def assess_live_adapter(
    plans: Iterable[LiveAdapterPlan],
    *,
    router_canary_report: Any | None,
    ingress_drain_report: Any | None,
    backpressure_report: Any,
    effect_ledger_report: Any | None,
    now: int,
    expected_mode: LiveAdapterMode,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    expected_frame_digest: bytes,
    expected_session_id: str,
    expected_destination: str,
    expected_caller_digest: bytes,
    expected_handler_digest: bytes,
    previous_seen_plan_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> LiveAdapterReport:
    plan_t = tuple(plans)
    mode = LiveAdapterMode(expected_mode)
    component_digests = (_component_digest(router_canary_report), _component_digest(ingress_drain_report), _component_digest(backpressure_report), _component_digest(effect_ledger_report))
    common = dict(mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, frame_digest=expected_frame_digest, session_id=expected_session_id, destination=expected_destination, caller_digest=expected_caller_digest, handler_digest=expected_handler_digest, plans=plan_t, components=component_digests)
    if not plan_t:
        return _report(LiveAdapterDecisionKind.EMPTY_NO_PLANS, False, False, "live adapter needs plans", **common)
    if _mode_needs_router(mode) and (not _component_accept(router_canary_report) or _component_quarantined(router_canary_report)):
        return _report(LiveAdapterDecisionKind.HOLD_ROUTER_CANARY if not _component_quarantined(router_canary_report) else LiveAdapterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "router canary required for outbound adapter", **common)
    if _mode_needs_ingress(mode) and (not _component_accept(ingress_drain_report) or _component_quarantined(ingress_drain_report)):
        return _report(LiveAdapterDecisionKind.HOLD_INGRESS_DRAIN if not _component_quarantined(ingress_drain_report) else LiveAdapterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "ingress drain required for inbound adapter", **common)
    if not _component_accept(backpressure_report) or _component_quarantined(backpressure_report):
        return _report(LiveAdapterDecisionKind.HOLD_BACKPRESSURE if not _component_quarantined(backpressure_report) else LiveAdapterDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "backpressure report must accept", **common)
    if mode in (LiveAdapterMode.OUTBOUND_PUBLIC_SEND, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) and (not _component_accept(effect_ledger_report) or _component_quarantined(effect_ledger_report)):
        return _report(LiveAdapterDecisionKind.HOLD_EFFECT_LEDGER if not _component_quarantined(effect_ledger_report) else LiveAdapterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "outbound adapter needs accepted effect ledger", **common)
    if any(_component_watch(component) for component in (router_canary_report, ingress_drain_report, backpressure_report, effect_ledger_report)) and not allow_component_watch:
        return _report(LiveAdapterDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried explicitly", **common)
    backpressure_mode = getattr(backpressure_report, "mode", None)
    if isinstance(backpressure_mode, BackpressureMode):
        if mode is LiveAdapterMode.OUTBOUND_PUBLIC_SEND and backpressure_mode is not BackpressureMode.OUTBOUND:
            return _report(LiveAdapterDecisionKind.QUARANTINE_BACKPRESSURE_MODE, False, False, "outbound adapter saw non-outbound backpressure", **common)
        if mode is LiveAdapterMode.INBOUND_HANDLER_WORK and backpressure_mode is not BackpressureMode.INBOUND:
            return _report(LiveAdapterDecisionKind.QUARANTINE_BACKPRESSURE_MODE, False, False, "inbound adapter saw non-inbound backpressure", **common)
        if mode is LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK and backpressure_mode is not BackpressureMode.BIDIRECTIONAL:
            return _report(LiveAdapterDecisionKind.QUARANTINE_BACKPRESSURE_MODE, False, False, "bidirectional adapter saw non-bidirectional backpressure", **common)

    seen = set(previous_seen_plan_digests)
    by_sequence: dict[int, LiveAdapterPlan] = {}
    for plan in plan_t:
        if not plan.verifies():
            return _report(LiveAdapterDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad live adapter signature", **common)
        if not plan.live(now):
            return _report(LiveAdapterDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future live adapter plan", **common)
        if plan.plan_digest in seen:
            return _report(LiveAdapterDecisionKind.QUARANTINE_REPLAY, False, False, "live adapter plan replayed", **common)
        if highest_seen_sequence is not None and plan.sequence < highest_seen_sequence:
            return _report(LiveAdapterDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "live adapter sequence rollback", **common)
        prior = by_sequence.get(plan.sequence)
        if prior is not None and prior.plan_core_digest != plan.plan_core_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence live adapter fork", **common)
        by_sequence[plan.sequence] = plan
        if plan.profile_id != expected_profile_id:
            return _report(LiveAdapterDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if plan.service_name != expected_service_name:
            return _report(LiveAdapterDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if plan.mode != mode:
            return _report(LiveAdapterDecisionKind.QUARANTINE_MODE_DRIFT, False, False, "mode drift", **common)
        if plan.scope_digest != expected_scope_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if plan.request_digest != expected_request_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if plan.public_payload_digest != expected_public_payload_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", **common)
        if plan.frame_digest != expected_frame_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_FRAME_DRIFT, False, False, "frame drift", **common)
        if plan.session_id != expected_session_id:
            return _report(LiveAdapterDecisionKind.QUARANTINE_SESSION_DRIFT, False, False, "session drift", **common)
        if plan.destination != expected_destination:
            return _report(LiveAdapterDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, False, "destination drift", **common)
        if plan.caller_digest != expected_caller_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_CALLER_DRIFT, False, False, "caller drift", **common)
        if plan.handler_digest != expected_handler_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_HANDLER_DRIFT, False, False, "handler drift", **common)
        if plan.router_canary_digest != component_digests[0] or plan.ingress_drain_digest != component_digests[1] or plan.backpressure_digest != component_digests[2] or plan.effect_ledger_digest != component_digests[3]:
            return _report(LiveAdapterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
        if not _mode_needs_router(mode) and plan.router_canary_digest != ZERO_DIGEST:
            return _report(LiveAdapterDecisionKind.QUARANTINE_MODE_COMPONENT_MISMATCH, False, False, "mode does not need router digest", **common)
        if not _mode_needs_ingress(mode) and plan.ingress_drain_digest != ZERO_DIGEST:
            return _report(LiveAdapterDecisionKind.QUARANTINE_MODE_COMPONENT_MISMATCH, False, False, "mode does not need ingress digest", **common)
        if mode is LiveAdapterMode.INBOUND_HANDLER_WORK and plan.effect_ledger_digest != ZERO_DIGEST:
            return _report(LiveAdapterDecisionKind.QUARANTINE_MODE_COMPONENT_MISMATCH, False, False, "inbound mode does not need effect ledger digest", **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_plan_digest != left.plan_digest:
            return _report(LiveAdapterDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "live adapter previous-link mismatch", **common)
    family_count = len({plan.family_id for plan in ordered})
    path_count = len({plan.path_family for plan in ordered})
    if family_count < min_family_count:
        return _report(LiveAdapterDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "live adapter needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(LiveAdapterDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "live adapter needs more path diversity", **common)
    latest = ordered[-1]
    component_watch = any(_component_watch(component) for component in (router_canary_report, ingress_drain_report, backpressure_report, effect_ledger_report))
    return _report(LiveAdapterDecisionKind.ACCEPT_WITH_WATCH if component_watch else LiveAdapterDecisionKind.ACCEPT_LIVE_ADAPTER, True, component_watch, "live adapter plan accepted", accepted=latest, **common)
