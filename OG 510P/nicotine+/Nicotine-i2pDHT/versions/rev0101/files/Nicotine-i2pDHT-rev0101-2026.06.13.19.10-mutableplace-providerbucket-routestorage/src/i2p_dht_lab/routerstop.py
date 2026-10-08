"""Router-stop shadow plans after service exit.

rev0041 treats stopping or retaining the local I2P router as a protocol boundary.
A service exit report may pause/demote/freeze a garden service, but it should not
silently stop a bundled router, discard persistent Destination state, or disable
cover/transit assumptions.  This is still a no-network shadow surface: it signs
small plans and pressure-tests them before any future SAM/i2pd side effect.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

ROUTER_STOP_DOMAIN = DOMAIN + b":router-stop-v1:"
ZERO_DIGEST = b"\x00" * 32


class RouterStopAction(str, Enum):
    STOP_SERVICE_SESSION = "stop_service_session"
    STOP_BUNDLED_ROUTER = "stop_bundled_router"
    KEEP_ROUTER_RUNNING = "keep_router_running"
    DISABLE_PUBLIC_BRIDGE = "disable_public_bridge"
    ENTER_OFFLINE_PROFILE = "enter_offline_profile"


class RouterStopDecisionKind(str, Enum):
    ACCEPT_SESSION_STOP = "accept_session_stop"
    ACCEPT_ROUTER_STOP = "accept_router_stop"
    ACCEPT_KEEP_ROUTER_RUNNING = "accept_keep_router_running"
    ACCEPT_BRIDGE_DISABLE = "accept_bridge_disable"
    HOLD_NO_PLAN = "hold_no_plan"
    HOLD_NEEDS_SERVICE_EXIT = "hold_needs_service_exit"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_ROUTER_DRIFT = "quarantine_router_drift"
    QUARANTINE_EXIT_REPORT_DRIFT = "quarantine_exit_report_drift"
    QUARANTINE_PUBLIC_BRIDGE_NOT_DRAINED = "quarantine_public_bridge_not_drained"
    QUARANTINE_EPHEMERAL_DESTINATION = "quarantine_ephemeral_destination"
    QUARANTINE_NOTRANSIT_REGRESSION = "quarantine_notransit_regression"


@dataclass(frozen=True)
class RouterStopPlan:
    action: RouterStopAction
    profile_id: str
    service_name: str
    session_id_digest: bytes
    router_report_digest: bytes
    service_exit_report_digest: bytes
    operator_intent_digest: bytes
    sequence: int
    previous_plan_digest: bytes
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    public_bridge_active: bool = False
    bridge_drain_report_digest: bytes = ZERO_DIGEST
    persisted_destination: bool = True
    notransit_requested: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("router stop sequence must be non-negative")
        for name, value in (
            ("session_id_digest", self.session_id_digest),
            ("router_report_digest", self.router_report_digest),
            ("service_exit_report_digest", self.service_exit_report_digest),
            ("operator_intent_digest", self.operator_intent_digest),
            ("previous_plan_digest", self.previous_plan_digest),
            ("bridge_drain_report_digest", self.bridge_drain_report_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("router stop plan expires_at must be after issued_at")
        if self.signature and len(self.signature) != 64:
            raise ValueError("router stop signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"session": self.session_id_digest,
            b"router": self.router_report_digest,
            b"exit": self.service_exit_report_digest,
            b"operator": self.operator_intent_digest,
            b"seq": self.sequence,
            b"prev": self.previous_plan_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"bridge_active": 1 if self.public_bridge_active else 0,
            b"bridge_drain": self.bridge_drain_report_digest,
            b"persisted_destination": 1 if self.persisted_destination else 0,
            b"notransit": 1 if self.notransit_requested else 0,
        }

    @property
    def plan_digest(self) -> bytes:
        return sha256(ROUTER_STOP_DOMAIN + b":digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return ROUTER_STOP_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def signed_bvalue(self) -> dict[bytes, BValue]:
        value = dict(self.unsigned_bvalue())
        value[b"sig"] = self.signature
        return value



def make_router_stop_plan(
    *,
    keypair: DhtKeypair,
    action: RouterStopAction,
    profile_id: str,
    service_name: str,
    session_id_digest: bytes,
    router_report_digest: bytes,
    service_exit_report_digest: bytes,
    operator_intent_digest: bytes,
    sequence: int,
    previous_plan_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    public_bridge_active: bool = False,
    bridge_drain_report_digest: bytes = ZERO_DIGEST,
    persisted_destination: bool = True,
    notransit_requested: bool = False,
) -> RouterStopPlan:
    plan = RouterStopPlan(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        session_id_digest=session_id_digest,
        router_report_digest=router_report_digest,
        service_exit_report_digest=service_exit_report_digest,
        operator_intent_digest=operator_intent_digest,
        sequence=sequence,
        previous_plan_digest=previous_plan_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        public_bridge_active=public_bridge_active,
        bridge_drain_report_digest=bridge_drain_report_digest,
        persisted_destination=persisted_destination,
        notransit_requested=notransit_requested,
    )
    return replace(plan, signature=keypair.sign(plan.signature_payload()))


@dataclass(frozen=True)
class RouterStopPolicy:
    require_service_exit_acceptance: bool = True
    require_bridge_drain_for_public_bridge: bool = True
    require_persistent_destination_for_router_stop: bool = True
    forbid_notransit_regression: bool = True


@dataclass(frozen=True)
class RouterStopReport:
    decision_kind: RouterStopDecisionKind
    accept: bool
    reason: str
    action: RouterStopAction | None
    profile_id: str | None
    service_name: str | None
    session_id_digest: bytes | None
    router_report_digest: bytes | None
    plan_digests: tuple[bytes, ...]
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def _report(kind: RouterStopDecisionKind, accept: bool, reason: str, plans: Iterable[RouterStopPlan], *, action: RouterStopAction | None = None) -> RouterStopReport:
    plan_tuple = tuple(sorted(plans, key=lambda item: (item.sequence, item.plan_digest)))
    latest = plan_tuple[-1] if plan_tuple else None
    digests = tuple(sorted(plan.plan_digest for plan in plan_tuple))
    highest = max((plan.sequence for plan in plan_tuple), default=-1)
    digest = sha256(ROUTER_STOP_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"action": action.value if action else "",
        b"profile": latest.profile_id if latest else "",
        b"service": latest.service_name if latest else "",
        b"session": latest.session_id_digest if latest else b"",
        b"router": latest.router_report_digest if latest else b"",
        b"highest": highest,
        b"plans": list(digests),
    }))
    return RouterStopReport(kind, accept, reason, action, latest.profile_id if latest else None, latest.service_name if latest else None, latest.session_id_digest if latest else None, latest.router_report_digest if latest else None, digests, highest, digest)



def assess_router_stop_plan(
    plans: Iterable[RouterStopPlan],
    *,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_session_id_digest: bytes,
    expected_router_report_digest: bytes,
    expected_service_exit_report_digest: bytes | None = None,
    service_exit_accepted: bool = False,
    bridge_drain_accepted: bool = False,
    previous_sequence: int | None = None,
    previous_plan_digest: bytes | None = None,
    previously_seen_plans: Iterable[bytes] = (),
    policy: RouterStopPolicy | None = None,
) -> RouterStopReport:
    policy = policy or RouterStopPolicy()
    plan_tuple = tuple(sorted(plans, key=lambda item: (item.sequence, item.plan_digest)))
    if not plan_tuple:
        return _report(RouterStopDecisionKind.HOLD_NO_PLAN, False, "no router stop plan", plan_tuple)
    if any(not plan.verifies() for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "router stop signature mismatch", plan_tuple)
    if any(plan.issued_at > now or plan.expires_at <= now for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "router stop plan outside local time window", plan_tuple)
    seen = set(previously_seen_plans)
    if any(plan.plan_digest in seen for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_REPLAY, False, "router stop plan replay", plan_tuple)
    if previous_sequence is not None and max(plan.sequence for plan in plan_tuple) < previous_sequence:
        return _report(RouterStopDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "router stop sequence rolled back", plan_tuple)
    by_sequence: dict[int, set[bytes]] = {}
    for plan in plan_tuple:
        by_sequence.setdefault(plan.sequence, set()).add(plan.plan_digest)
    if any(len(digests) > 1 for digests in by_sequence.values()):
        return _report(RouterStopDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "router stop sequence fork", plan_tuple)
    if previous_plan_digest is not None:
        first = plan_tuple[0]
        if first.sequence > 0 and first.previous_plan_digest != previous_plan_digest:
            return _report(RouterStopDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "router stop previous link mismatch", plan_tuple)
    for prior, current in zip(plan_tuple, plan_tuple[1:]):
        if current.sequence > prior.sequence and current.previous_plan_digest != prior.plan_digest:
            return _report(RouterStopDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "router stop internal previous link mismatch", plan_tuple)
    if any(plan.profile_id != expected_profile_id for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "router stop profile drift", plan_tuple)
    if any(plan.service_name != expected_service_name for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "router stop service drift", plan_tuple)
    if any(plan.session_id_digest != expected_session_id_digest for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_SESSION_DRIFT, False, "router stop session drift", plan_tuple)
    if any(plan.router_report_digest != expected_router_report_digest for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_ROUTER_DRIFT, False, "router stop router-report drift", plan_tuple)
    if expected_service_exit_report_digest is not None and any(plan.service_exit_report_digest != expected_service_exit_report_digest for plan in plan_tuple):
        return _report(RouterStopDecisionKind.QUARANTINE_EXIT_REPORT_DRIFT, False, "router stop exit-report drift", plan_tuple)
    latest = plan_tuple[-1]
    if policy.require_service_exit_acceptance and not service_exit_accepted and latest.action is not RouterStopAction.KEEP_ROUTER_RUNNING:
        return _report(RouterStopDecisionKind.HOLD_NEEDS_SERVICE_EXIT, False, "router side effect needs accepted service exit", plan_tuple, action=latest.action)
    if policy.forbid_notransit_regression and latest.notransit_requested and latest.action in {RouterStopAction.KEEP_ROUTER_RUNNING, RouterStopAction.STOP_SERVICE_SESSION}:
        return _report(RouterStopDecisionKind.QUARANTINE_NOTRANSIT_REGRESSION, False, "router plan would regress cover/transit assumption", plan_tuple, action=latest.action)
    if latest.action is RouterStopAction.STOP_BUNDLED_ROUTER:
        if policy.require_persistent_destination_for_router_stop and not latest.persisted_destination:
            return _report(RouterStopDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION, False, "router stop would discard ephemeral destination", plan_tuple, action=latest.action)
        if latest.public_bridge_active and policy.require_bridge_drain_for_public_bridge and not bridge_drain_accepted:
            return _report(RouterStopDecisionKind.QUARANTINE_PUBLIC_BRIDGE_NOT_DRAINED, False, "public bridge router stop needs drain", plan_tuple, action=latest.action)
        return _report(RouterStopDecisionKind.ACCEPT_ROUTER_STOP, True, "router stop shadow accepted", plan_tuple, action=latest.action)
    if latest.action is RouterStopAction.STOP_SERVICE_SESSION:
        return _report(RouterStopDecisionKind.ACCEPT_SESSION_STOP, True, "service session stop shadow accepted", plan_tuple, action=latest.action)
    if latest.action is RouterStopAction.KEEP_ROUTER_RUNNING:
        return _report(RouterStopDecisionKind.ACCEPT_KEEP_ROUTER_RUNNING, True, "router retained for cover/contribution", plan_tuple, action=latest.action)
    if latest.action is RouterStopAction.DISABLE_PUBLIC_BRIDGE:
        if latest.public_bridge_active and policy.require_bridge_drain_for_public_bridge and not bridge_drain_accepted:
            return _report(RouterStopDecisionKind.QUARANTINE_PUBLIC_BRIDGE_NOT_DRAINED, False, "bridge disable needs accepted drain", plan_tuple, action=latest.action)
        return _report(RouterStopDecisionKind.ACCEPT_BRIDGE_DISABLE, True, "public bridge disable shadow accepted", plan_tuple, action=latest.action)
    return _report(RouterStopDecisionKind.ACCEPT_SESSION_STOP, True, "offline-profile transition accepted as session stop", plan_tuple, action=latest.action)
