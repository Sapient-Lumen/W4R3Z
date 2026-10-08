"""Multi-service router/session interaction pressure.

rev0042 treats a shared router as a joined boundary.  A single garden service
may be ready to pause, stop, or disable bridge exposure, but that does not mean
that the bundled router or shared session state can be changed safely while
sibling services remain active.  This module is intentionally no-network and
small: it signs service runtime observations and pressure-tests a requested
control action against all visible services.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

MULTISERVICE_DOMAIN = DOMAIN + b":multiservice-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceRuntimeState(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    DRAINING = "draining"
    PAUSED = "paused"
    FROZEN = "frozen"
    STOPPED = "stopped"


class MultiServiceAction(str, Enum):
    STOP_ONE_SESSION = "stop_one_session"
    STOP_BUNDLED_ROUTER = "stop_bundled_router"
    KEEP_ROUTER_RUNNING = "keep_router_running"
    DISABLE_PUBLIC_BRIDGE = "disable_public_bridge"
    ENTER_OFFLINE_PROFILE = "enter_offline_profile"


class MultiServiceDecisionKind(str, Enum):
    ACCEPT_ISOLATED_SERVICE_ACTION = "accept_isolated_service_action"
    ACCEPT_SHARED_ROUTER_ACTION = "accept_shared_router_action"
    ACCEPT_KEEP_ROUTER_RUNNING = "accept_keep_router_running"
    HOLD_NO_OBSERVATIONS = "hold_no_observations"
    HOLD_TARGET_NOT_VISIBLE = "hold_target_not_visible"
    HOLD_TARGET_STILL_ACTIVE = "hold_target_still_active"
    HOLD_ACTIVE_SIBLING_SERVICES = "hold_active_sibling_services"
    HOLD_PUBLIC_BRIDGE_STILL_ACTIVE = "hold_public_bridge_still_active"
    HOLD_LOW_SERVICE_FAMILY_DIVERSITY = "hold_low_service_family_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_ROUTER_DRIFT = "quarantine_router_drift"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"


@dataclass(frozen=True)
class ServiceRuntimeObservation:
    service_name: str
    profile_id: str
    session_id_digest: bytes
    router_report_digest: bytes
    state: ServiceRuntimeState
    sequence: int
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    family_id: str
    path_family: str
    public_bridge_active: bool = False
    profile_cooldown_digest: bytes = ZERO_DIGEST
    operator_key_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.profile_id or len(self.profile_id.encode("utf-8")) > 80:
            raise ValueError("profile_id must be short and non-empty")
        if not self.family_id or not self.path_family:
            raise ValueError("family and path family must be non-empty")
        if self.sequence < 0:
            raise ValueError("service observation sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("service observation must expire after issue")
        for name, value in (
            ("session_id_digest", self.session_id_digest),
            ("router_report_digest", self.router_report_digest),
            ("profile_cooldown_digest", self.profile_cooldown_digest),
            ("operator_key_digest", self.operator_key_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("service runtime signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"service": self.service_name,
            b"profile": self.profile_id,
            b"session": self.session_id_digest,
            b"router": self.router_report_digest,
            b"state": self.state.value,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"signer": self.signer_public_key,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"public_bridge": 1 if self.public_bridge_active else 0,
            b"cooldown": self.profile_cooldown_digest,
            b"operator_key": self.operator_key_digest,
        }

    @property
    def observation_digest(self) -> bytes:
        return sha256(MULTISERVICE_DOMAIN + b":obs-digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return MULTISERVICE_DOMAIN + b":obs-sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)


@dataclass(frozen=True)
class MultiServicePolicy:
    min_family_diversity_for_shared_router: int = 2
    min_path_diversity_for_shared_router: int = 2
    require_target_drain_for_session_stop: bool = True
    require_no_public_bridge_for_router_stop: bool = True


@dataclass(frozen=True)
class MultiServiceReport:
    decision_kind: MultiServiceDecisionKind
    accept: bool
    reason: str
    action: MultiServiceAction
    target_service: str
    visible_services: tuple[str, ...]
    active_sibling_services: tuple[str, ...]
    public_bridge_services: tuple[str, ...]
    observation_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


_ACTIVE_STATES = {ServiceRuntimeState.ACTIVE, ServiceRuntimeState.DEGRADED}
_READY_TO_STOP = {ServiceRuntimeState.DRAINING, ServiceRuntimeState.PAUSED, ServiceRuntimeState.FROZEN, ServiceRuntimeState.STOPPED}


def make_service_runtime_observation(
    *,
    keypair: DhtKeypair,
    service_name: str,
    profile_id: str,
    session_id_digest: bytes,
    router_report_digest: bytes,
    state: ServiceRuntimeState,
    sequence: int,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    public_bridge_active: bool = False,
    profile_cooldown_digest: bytes = ZERO_DIGEST,
    operator_key_digest: bytes = ZERO_DIGEST,
) -> ServiceRuntimeObservation:
    observation = ServiceRuntimeObservation(
        service_name=service_name,
        profile_id=profile_id,
        session_id_digest=session_id_digest,
        router_report_digest=router_report_digest,
        state=state,
        sequence=sequence,
        issued_at=issued_at,
        expires_at=expires_at,
        signer_public_key=keypair.public_key_bytes,
        family_id=family_id,
        path_family=path_family,
        public_bridge_active=public_bridge_active,
        profile_cooldown_digest=profile_cooldown_digest,
        operator_key_digest=operator_key_digest,
    )
    return replace(observation, signature=keypair.sign(observation.signature_payload()))


def _make_report(kind: MultiServiceDecisionKind, accept: bool, reason: str, action: MultiServiceAction, target_service: str, observations: Iterable[ServiceRuntimeObservation]) -> MultiServiceReport:
    obs = tuple(sorted(observations, key=lambda item: (item.service_name, item.sequence, item.observation_digest)))
    visible = tuple(sorted({item.service_name for item in obs}))
    active_siblings = tuple(sorted({item.service_name for item in obs if item.service_name != target_service and item.state in _ACTIVE_STATES}))
    public_bridges = tuple(sorted({item.service_name for item in obs if item.public_bridge_active}))
    digests = tuple(sorted(item.observation_digest for item in obs))
    digest = sha256(MULTISERVICE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"action": action.value,
        b"target": target_service,
        b"visible": list(visible),
        b"active_siblings": list(active_siblings),
        b"public_bridges": list(public_bridges),
        b"obs": list(digests),
    }))
    return MultiServiceReport(kind, accept, reason, action, target_service, visible, active_siblings, public_bridges, digests, digest)


def assess_multi_service_action(
    observations: Iterable[ServiceRuntimeObservation],
    *,
    now: int,
    action: MultiServiceAction,
    target_service: str,
    expected_profile_id: str,
    expected_router_report_digest: bytes,
    expected_session_id_digest: bytes | None = None,
    previously_seen_observations: Iterable[bytes] = (),
    policy: MultiServicePolicy | None = None,
) -> MultiServiceReport:
    policy = policy or MultiServicePolicy()
    obs = tuple(sorted(observations, key=lambda item: (item.service_name, item.sequence, item.observation_digest)))
    if not obs:
        return _make_report(MultiServiceDecisionKind.HOLD_NO_OBSERVATIONS, False, "no service runtime observations", action, target_service, obs)
    seen = set(previously_seen_observations)
    for item in obs:
        if not item.verifies():
            return _make_report(MultiServiceDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad service observation signature", action, target_service, obs)
        if item.issued_at > now or item.expires_at <= now:
            return _make_report(MultiServiceDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "service observation expired or from the future", action, target_service, obs)
        if item.observation_digest in seen:
            return _make_report(MultiServiceDecisionKind.QUARANTINE_REPLAY, False, "service observation replay", action, target_service, obs)
        if item.profile_id != expected_profile_id:
            return _make_report(MultiServiceDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "profile drift across service observations", action, target_service, obs)
        if item.router_report_digest != expected_router_report_digest:
            return _make_report(MultiServiceDecisionKind.QUARANTINE_ROUTER_DRIFT, False, "router report drift across service observations", action, target_service, obs)
        if expected_session_id_digest is not None and item.service_name == target_service and item.session_id_digest != expected_session_id_digest:
            return _make_report(MultiServiceDecisionKind.QUARANTINE_SESSION_DRIFT, False, "target session drift", action, target_service, obs)
    by_service: dict[str, list[ServiceRuntimeObservation]] = {}
    for item in obs:
        by_service.setdefault(item.service_name, []).append(item)
    for service, items in by_service.items():
        seq_to_digest: dict[int, bytes] = {}
        for item in items:
            previous = seq_to_digest.setdefault(item.sequence, item.observation_digest)
            if previous != item.observation_digest:
                return _make_report(MultiServiceDecisionKind.QUARANTINE_SEQUENCE_FORK, False, f"same-sequence service observation fork for {service}", action, target_service, obs)
    target_items = by_service.get(target_service, [])
    if not target_items:
        return _make_report(MultiServiceDecisionKind.HOLD_TARGET_NOT_VISIBLE, False, "target service is not visible", action, target_service, obs)
    latest_by_service = {service: max(items, key=lambda item: (item.sequence, item.issued_at, item.observation_digest)) for service, items in by_service.items()}
    target = latest_by_service[target_service]
    if action is MultiServiceAction.KEEP_ROUTER_RUNNING:
        return _make_report(MultiServiceDecisionKind.ACCEPT_KEEP_ROUTER_RUNNING, True, "shared router retained", action, target_service, obs)
    if action is MultiServiceAction.STOP_ONE_SESSION:
        if policy.require_target_drain_for_session_stop and target.state not in _READY_TO_STOP:
            return _make_report(MultiServiceDecisionKind.HOLD_TARGET_STILL_ACTIVE, False, "target service is not drained/paused/frozen/stopped", action, target_service, obs)
        return _make_report(MultiServiceDecisionKind.ACCEPT_ISOLATED_SERVICE_ACTION, True, "target service can stop without touching shared router", action, target_service, obs)
    active_siblings = tuple(sorted(service for service, item in latest_by_service.items() if service != target_service and item.state in _ACTIVE_STATES))
    if action in (MultiServiceAction.STOP_BUNDLED_ROUTER, MultiServiceAction.ENTER_OFFLINE_PROFILE):
        if active_siblings:
            return _make_report(MultiServiceDecisionKind.HOLD_ACTIVE_SIBLING_SERVICES, False, "sibling services still require the shared router", action, target_service, obs)
        if policy.require_no_public_bridge_for_router_stop and any(item.public_bridge_active for item in latest_by_service.values()):
            return _make_report(MultiServiceDecisionKind.HOLD_PUBLIC_BRIDGE_STILL_ACTIVE, False, "public bridge exposure remains active", action, target_service, obs)
        families = {item.family_id for item in latest_by_service.values()}
        paths = {item.path_family for item in latest_by_service.values()}
        if len(families) < policy.min_family_diversity_for_shared_router or len(paths) < policy.min_path_diversity_for_shared_router:
            return _make_report(MultiServiceDecisionKind.HOLD_LOW_SERVICE_FAMILY_DIVERSITY, False, "shared-router decision lacks service/path diversity", action, target_service, obs)
        return _make_report(MultiServiceDecisionKind.ACCEPT_SHARED_ROUTER_ACTION, True, "all visible services permit shared-router action", action, target_service, obs)
    if action is MultiServiceAction.DISABLE_PUBLIC_BRIDGE:
        if target.public_bridge_active:
            return _make_report(MultiServiceDecisionKind.HOLD_PUBLIC_BRIDGE_STILL_ACTIVE, False, "target public bridge still reports active exposure", action, target_service, obs)
        return _make_report(MultiServiceDecisionKind.ACCEPT_ISOLATED_SERVICE_ACTION, True, "target public bridge exposure is disabled without stopping router", action, target_service, obs)
    raise ValueError(f"unknown multi-service action: {action}")
