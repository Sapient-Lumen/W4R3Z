"""Router canary boundary before any live SAM-backed public-edge send.

rev0050 added a SAM canary that binds frame/idempotency/egress/outbox drain
before a future send.  rev0051 adds a second no-network seam: the router/session
itself must still look like the same durable, contribution-safe, non-leaky
profile that the bundle/start lanes accepted.

This module does not open a SAM socket and does not claim router correctness. It
makes the most dangerous assumptions explicit and testable: persistent
Destination state, no accidental proxy exposure, no quiet notransit regression,
endpoint/session stability, and exact-boundary binding to the sam-canary report.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

ROUTER_CANARY_DOMAIN = DOMAIN + b":router-canary-v1:"


class RouterCanaryAction(str, Enum):
    PUBLIC_REFRESH = "public_refresh"
    PUBLIC_WITHDRAW = "public_withdraw"
    PUBLIC_REPAIR = "public_repair"


class RouterCanaryDecisionKind(str, Enum):
    ACCEPT_ROUTER_CANARY = "accept_router_canary"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_SAM_CANARY = "hold_sam_canary"
    HOLD_ROUTER_HARNESS = "hold_router_harness"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_FRAME_DRIFT = "quarantine_frame_drift"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_ENDPOINT_DRIFT = "quarantine_endpoint_drift"
    QUARANTINE_ROUTER_PROFILE_DRIFT = "quarantine_router_profile_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_EPHEMERAL_DESTINATION = "quarantine_ephemeral_destination"
    QUARANTINE_PROXY_EXPOSURE = "quarantine_proxy_exposure"
    QUARANTINE_NOTRANSIT_REGRESSION = "quarantine_notransit_regression"
    QUARANTINE_ROUTER_UNREADY = "quarantine_router_unready"


@dataclass(frozen=True)
class RouterCanaryObservation:
    action: RouterCanaryAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    frame_digest: bytes
    sam_canary_digest: bytes
    router_harness_digest: bytes
    outbox_drain_digest: bytes
    session_id: str
    destination: str
    sam_endpoint: str
    router_profile_digest: bytes
    router_ready: bool
    destination_persistent: bool
    transit_enabled: bool
    http_proxy_enabled: bool
    socks_proxy_enabled: bool
    sequence: int
    previous_observation_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", RouterCanaryAction(self.action))
        if not self.profile_id or not self.service_name or not self.session_id or not self.destination or not self.sam_endpoint:
            raise ValueError("router canary needs profile/service/session/destination/endpoint")
        if not self.family_id or not self.path_family:
            raise ValueError("router canary needs family/path family")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("frame_digest", self.frame_digest),
            ("sam_canary_digest", self.sam_canary_digest),
            ("router_harness_digest", self.router_harness_digest),
            ("outbox_drain_digest", self.outbox_drain_digest),
            ("router_profile_digest", self.router_profile_digest),
            ("previous_observation_digest", self.previous_observation_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"frame": self.frame_digest,
            b"sam_canary": self.sam_canary_digest,
            b"router_harness": self.router_harness_digest,
            b"outbox_drain": self.outbox_drain_digest,
            b"session": self.session_id,
            b"destination": self.destination,
            b"endpoint": self.sam_endpoint,
            b"router_profile": self.router_profile_digest,
            b"ready": 1 if self.router_ready else 0,
            b"persistent": 1 if self.destination_persistent else 0,
            b"transit": 1 if self.transit_enabled else 0,
            b"http_proxy": 1 if self.http_proxy_enabled else 0,
            b"socks_proxy": 1 if self.socks_proxy_enabled else 0,
            b"seq": self.sequence,
            b"prev": self.previous_observation_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return ROUTER_CANARY_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(ROUTER_CANARY_DOMAIN + b":observation-core:" + bencode(self.unsigned_bvalue()))

    @property
    def observation_digest(self) -> bytes:
        return sha256(ROUTER_CANARY_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class RouterCanaryReport:
    decision_kind: RouterCanaryDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: RouterCanaryAction
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    frame_digest: bytes
    session_id: str
    destination: str
    sam_endpoint: str
    router_profile_digest: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _component_digest(report: Any) -> bytes:
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks 32-byte digest")


def _component_accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def make_router_canary_observation(
    *,
    keypair: DhtKeypair,
    action: RouterCanaryAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    frame_digest: bytes,
    sam_canary_digest: bytes,
    router_harness_digest: bytes,
    outbox_drain_digest: bytes,
    session_id: str,
    destination: str,
    sam_endpoint: str,
    router_profile_digest: bytes,
    router_ready: bool,
    destination_persistent: bool,
    transit_enabled: bool,
    http_proxy_enabled: bool,
    socks_proxy_enabled: bool,
    sequence: int,
    previous_observation_digest: bytes = ZERO_DIGEST,
    issued_at: int = 0,
    expires_at: int = 1,
    family_id: str = "family-default",
    path_family: str = "path-default",
) -> RouterCanaryObservation:
    unsigned = RouterCanaryObservation(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        payload_digest=payload_digest,
        frame_digest=frame_digest,
        sam_canary_digest=sam_canary_digest,
        router_harness_digest=router_harness_digest,
        outbox_drain_digest=outbox_drain_digest,
        session_id=session_id,
        destination=destination,
        sam_endpoint=sam_endpoint,
        router_profile_digest=router_profile_digest,
        router_ready=router_ready,
        destination_persistent=destination_persistent,
        transit_enabled=transit_enabled,
        http_proxy_enabled=http_proxy_enabled,
        socks_proxy_enabled=socks_proxy_enabled,
        sequence=sequence,
        previous_observation_digest=previous_observation_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(
    kind: RouterCanaryDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    expected_profile_id: str,
    expected_service_name: str,
    expected_action: RouterCanaryAction,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_frame_digest: bytes,
    expected_session_id: str,
    expected_destination: str,
    expected_sam_endpoint: str,
    expected_router_profile_digest: bytes,
    accepted: RouterCanaryObservation | None = None,
    observations: Iterable[RouterCanaryObservation] = (),
    components: Iterable[bytes] = (),
) -> RouterCanaryReport:
    obs = tuple(observations)
    digests = tuple(observation.observation_digest for observation in obs)
    families = {observation.family_id for observation in obs}
    paths = {observation.path_family for observation in obs}
    highest = max((observation.sequence for observation in obs), default=-1)
    accepted_digest = accepted.observation_digest if accepted else ZERO_DIGEST
    component_t = tuple(components)
    digest = sha256(ROUTER_CANARY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": expected_profile_id,
        b"service": expected_service_name,
        b"action": expected_action.value,
        b"scope": expected_scope_digest,
        b"request": expected_request_digest,
        b"payload": expected_payload_digest,
        b"frame": expected_frame_digest,
        b"session": expected_session_id,
        b"destination": expected_destination,
        b"endpoint": expected_sam_endpoint,
        b"router_profile": expected_router_profile_digest,
        b"accepted": accepted_digest,
        b"observations": list(digests),
        b"components": list(component_t),
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return RouterCanaryReport(kind, accept, watch, reason, expected_profile_id, expected_service_name, expected_action, expected_scope_digest, expected_request_digest, expected_payload_digest, expected_frame_digest, expected_session_id, expected_destination, expected_sam_endpoint, expected_router_profile_digest, accepted_digest, digests, component_t, len(families), len(paths), highest, digest)


def assess_router_canary(
    observations: Iterable[RouterCanaryObservation],
    *,
    sam_canary_report: Any,
    router_harness_report: Any,
    outbox_drain_report: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_action: RouterCanaryAction,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_frame_digest: bytes,
    expected_session_id: str,
    expected_destination: str,
    expected_sam_endpoint: str,
    expected_router_profile_digest: bytes,
    previous_seen_observation_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    require_transit_for_public_bridge: bool = True,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> RouterCanaryReport:
    obs = tuple(observations)
    component_digests = (_component_digest(sam_canary_report), _component_digest(router_harness_report), _component_digest(outbox_drain_report))
    common = dict(
        expected_profile_id=expected_profile_id,
        expected_service_name=expected_service_name,
        expected_action=expected_action,
        expected_scope_digest=expected_scope_digest,
        expected_request_digest=expected_request_digest,
        expected_payload_digest=expected_payload_digest,
        expected_frame_digest=expected_frame_digest,
        expected_session_id=expected_session_id,
        expected_destination=expected_destination,
        expected_sam_endpoint=expected_sam_endpoint,
        expected_router_profile_digest=expected_router_profile_digest,
        observations=obs,
        components=component_digests,
    )
    if not obs:
        return _report(RouterCanaryDecisionKind.EMPTY_NO_OBSERVATIONS, False, False, "router canary needs observations", **common)
    if not _component_accept(sam_canary_report) or _component_quarantined(sam_canary_report):
        return _report(RouterCanaryDecisionKind.HOLD_SAM_CANARY if not _component_quarantined(sam_canary_report) else RouterCanaryDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "router canary requires accepted SAM canary report", **common)
    if not _component_accept(router_harness_report) or _component_quarantined(router_harness_report):
        return _report(RouterCanaryDecisionKind.HOLD_ROUTER_HARNESS if not _component_quarantined(router_harness_report) else RouterCanaryDecisionKind.QUARANTINE_ROUTER_UNREADY, False, False, "router canary requires accepted router harness report", **common)
    if not _component_accept(outbox_drain_report) or _component_quarantined(outbox_drain_report):
        return _report(RouterCanaryDecisionKind.HOLD_SAM_CANARY if not _component_quarantined(outbox_drain_report) else RouterCanaryDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "router canary requires accepted outbox drain report", **common)
    if any(_component_watch(component) for component in (sam_canary_report, router_harness_report, outbox_drain_report)) and not allow_component_watch:
        return _report(RouterCanaryDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried explicitly", **common)

    seen = set(previous_seen_observation_digests)
    by_sequence: dict[int, RouterCanaryObservation] = {}
    previous_by_sequence: dict[int, bytes] = {}
    for observation in obs:
        if not observation.verifies():
            return _report(RouterCanaryDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad router canary signature", **common)
        if not observation.live(now):
            return _report(RouterCanaryDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future router canary observation", **common)
        if observation.observation_digest in seen:
            return _report(RouterCanaryDecisionKind.QUARANTINE_REPLAY, False, False, "router canary observation replayed", **common)
        if highest_seen_sequence is not None and observation.sequence < highest_seen_sequence:
            return _report(RouterCanaryDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "router canary sequence rolled back", **common)
        prior = by_sequence.get(observation.sequence)
        if prior is not None and prior.observation_core_digest != observation.observation_core_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence router canary fork", **common)
        by_sequence[observation.sequence] = observation
        previous_by_sequence[observation.sequence] = observation.previous_observation_digest
        if observation.profile_id != expected_profile_id:
            return _report(RouterCanaryDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if observation.service_name != expected_service_name:
            return _report(RouterCanaryDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if observation.action != expected_action:
            return _report(RouterCanaryDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "action drift", **common)
        if observation.scope_digest != expected_scope_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if observation.request_digest != expected_request_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if observation.payload_digest != expected_payload_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", **common)
        if observation.frame_digest != expected_frame_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_FRAME_DRIFT, False, False, "frame drift", **common)
        if observation.session_id != expected_session_id:
            return _report(RouterCanaryDecisionKind.QUARANTINE_SESSION_DRIFT, False, False, "session drift", **common)
        if observation.destination != expected_destination:
            return _report(RouterCanaryDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, False, "destination drift", **common)
        if observation.sam_endpoint != expected_sam_endpoint:
            return _report(RouterCanaryDecisionKind.QUARANTINE_ENDPOINT_DRIFT, False, False, "SAM endpoint drift", **common)
        if observation.router_profile_digest != expected_router_profile_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_ROUTER_PROFILE_DRIFT, False, False, "router profile digest drift", **common)
        if observation.sam_canary_digest != component_digests[0] or observation.router_harness_digest != component_digests[1] or observation.outbox_drain_digest != component_digests[2]:
            return _report(RouterCanaryDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
        if not observation.router_ready:
            return _report(RouterCanaryDecisionKind.QUARANTINE_ROUTER_UNREADY, False, False, "router is not ready", **common)
        if not observation.destination_persistent:
            return _report(RouterCanaryDecisionKind.QUARANTINE_EPHEMERAL_DESTINATION, False, False, "ephemeral Destination state at public edge", **common)
        if observation.http_proxy_enabled or observation.socks_proxy_enabled:
            return _report(RouterCanaryDecisionKind.QUARANTINE_PROXY_EXPOSURE, False, False, "public-edge canary saw proxy exposure", **common)
        if require_transit_for_public_bridge and not observation.transit_enabled:
            return _report(RouterCanaryDecisionKind.QUARANTINE_NOTRANSIT_REGRESSION, False, False, "public bridge refresh would quietly disable transit", **common)

    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_observation_digest != left.observation_digest:
            return _report(RouterCanaryDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "router canary previous-link mismatch", **common)
    family_count = len({observation.family_id for observation in obs})
    path_count = len({observation.path_family for observation in obs})
    if family_count < min_family_count:
        return _report(RouterCanaryDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "router canary needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(RouterCanaryDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "router canary needs more path diversity", **common)
    latest = ordered[-1]
    watch = any(_component_watch(component) for component in (sam_canary_report, router_harness_report, outbox_drain_report))
    return _report(RouterCanaryDecisionKind.ACCEPT_WITH_WATCH if watch else RouterCanaryDecisionKind.ACCEPT_ROUTER_CANARY, True, watch, "router canary accepted", accepted=latest, **common)
