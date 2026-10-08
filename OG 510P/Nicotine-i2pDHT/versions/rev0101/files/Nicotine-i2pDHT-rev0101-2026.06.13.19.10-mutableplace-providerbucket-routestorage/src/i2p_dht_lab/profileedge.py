"""Profile-edge join for future live side effects.

rev0052 gives the no-network live adapter one more guard: a profile-edge capsule
that binds live-adapter acceptance, shared backpressure, router/ingress reports,
profile budget, and hard-negative scans at one profile/service/scope/request
boundary.  It is a rehearsal artifact, not a live dispatcher.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .liveadapter import LiveAdapterMode
from .moderationquarantine import ZERO_DIGEST

PROFILE_EDGE_DOMAIN = DOMAIN + b":profile-edge-v1:"


class ProfileEdgeDecisionKind(str, Enum):
    ACCEPT_PROFILE_EDGE = "accept_profile_edge"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_LIVE_ADAPTER = "hold_live_adapter"
    HOLD_BACKPRESSURE = "hold_backpressure"
    HOLD_ROUTER_CANARY = "hold_router_canary"
    HOLD_INGRESS_DRAIN = "hold_ingress_drain"
    HOLD_PROFILE_BUDGET = "hold_profile_budget"
    HOLD_NEGATIVE_SCAN = "hold_negative_scan"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_CAPSULES = "empty_no_capsules"
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
    QUARANTINE_GENERATION_ROLLBACK = "quarantine_generation_rollback"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_EDGE_BUDGET_EXCEEDED = "quarantine_edge_budget_exceeded"


@dataclass(frozen=True)
class ProfileEdgeCapsule:
    mode: LiveAdapterMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    live_adapter_digest: bytes
    backpressure_digest: bytes
    router_canary_digest: bytes
    ingress_drain_digest: bytes
    profile_budget_digest: bytes
    negative_scan_digest: bytes
    profile_generation: int
    service_generation: int
    edge_budget_units: int
    hard_negative_count: int
    sequence: int
    previous_capsule_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", LiveAdapterMode(self.mode))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("profile-edge capsule needs profile/service/family/path")
        for name in ("profile_generation", "service_generation", "edge_budget_units", "hard_negative_count", "sequence"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("live_adapter_digest", self.live_adapter_digest),
            ("backpressure_digest", self.backpressure_digest),
            ("router_canary_digest", self.router_canary_digest),
            ("ingress_drain_digest", self.ingress_drain_digest),
            ("profile_budget_digest", self.profile_budget_digest),
            ("negative_scan_digest", self.negative_scan_digest),
            ("previous_capsule_digest", self.previous_capsule_digest),
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
            b"adapter": self.live_adapter_digest,
            b"backpressure": self.backpressure_digest,
            b"router": self.router_canary_digest,
            b"ingress": self.ingress_drain_digest,
            b"profile_budget": self.profile_budget_digest,
            b"negative_scan": self.negative_scan_digest,
            b"profile_generation": self.profile_generation,
            b"service_generation": self.service_generation,
            b"edge_budget": self.edge_budget_units,
            b"hard_negatives": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_capsule_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return PROFILE_EDGE_DOMAIN + b":capsule-sig:" + bencode(self.unsigned_bvalue())

    @property
    def capsule_core_digest(self) -> bytes:
        return sha256(PROFILE_EDGE_DOMAIN + b":capsule-core:" + bencode(self.unsigned_bvalue()))

    @property
    def capsule_digest(self) -> bytes:
        return sha256(PROFILE_EDGE_DOMAIN + b":capsule-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class ProfileEdgeReport:
    decision_kind: ProfileEdgeDecisionKind
    accept: bool
    watch: bool
    reason: str
    mode: LiveAdapterMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    public_payload_digest: bytes
    accepted_capsule_digest: bytes
    capsule_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    profile_generation: int
    service_generation: int
    total_edge_budget_units: int
    hard_negative_count: int
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


def make_profile_edge_capsule(
    *,
    keypair: DhtKeypair,
    mode: LiveAdapterMode,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    public_payload_digest: bytes,
    live_adapter_report: Any,
    backpressure_report: Any,
    router_canary_report: Any | None,
    ingress_drain_report: Any | None,
    profile_budget_report: Any,
    negative_scan_report: Any,
    profile_generation: int,
    service_generation: int,
    edge_budget_units: int,
    hard_negative_count: int,
    sequence: int,
    previous_capsule_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> ProfileEdgeCapsule:
    unsigned = ProfileEdgeCapsule(
        mode=mode,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        public_payload_digest=public_payload_digest,
        live_adapter_digest=_component_digest(live_adapter_report),
        backpressure_digest=_component_digest(backpressure_report),
        router_canary_digest=_component_digest(router_canary_report),
        ingress_drain_digest=_component_digest(ingress_drain_report),
        profile_budget_digest=_component_digest(profile_budget_report),
        negative_scan_digest=_component_digest(negative_scan_report),
        profile_generation=profile_generation,
        service_generation=service_generation,
        edge_budget_units=edge_budget_units,
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_capsule_digest=previous_capsule_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(
    kind: ProfileEdgeDecisionKind,
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
    accepted: ProfileEdgeCapsule | None = None,
    capsules: Iterable[ProfileEdgeCapsule] = (),
    components: Iterable[bytes] = (),
) -> ProfileEdgeReport:
    capsule_t = tuple(capsules)
    digests = tuple(capsule.capsule_digest for capsule in capsule_t)
    families = {capsule.family_id for capsule in capsule_t}
    paths = {capsule.path_family for capsule in capsule_t}
    highest = max((capsule.sequence for capsule in capsule_t), default=-1)
    profile_generation = max((capsule.profile_generation for capsule in capsule_t), default=-1)
    service_generation = max((capsule.service_generation for capsule in capsule_t), default=-1)
    total_budget = sum(capsule.edge_budget_units for capsule in capsule_t)
    hard_negatives = sum(capsule.hard_negative_count for capsule in capsule_t)
    accepted_digest = accepted.capsule_digest if accepted else ZERO_DIGEST
    component_t = tuple(components)
    digest = sha256(PROFILE_EDGE_DOMAIN + b":report:" + bencode({
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
        b"accepted": accepted_digest,
        b"capsules": list(digests),
        b"components": list(component_t),
        b"profile_generation": profile_generation,
        b"service_generation": service_generation,
        b"edge_budget": total_budget,
        b"hard_negatives": hard_negatives,
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return ProfileEdgeReport(kind, accept, watch, reason, mode, profile_id, service_name, scope_digest, request_digest, public_payload_digest, accepted_digest, digests, component_t, profile_generation, service_generation, total_budget, hard_negatives, len(families), len(paths), highest, digest)


def assess_profile_edge(
    capsules: Iterable[ProfileEdgeCapsule],
    *,
    live_adapter_report: Any,
    backpressure_report: Any,
    router_canary_report: Any | None,
    ingress_drain_report: Any | None,
    profile_budget_report: Any,
    negative_scan_report: Any,
    now: int,
    expected_mode: LiveAdapterMode,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_public_payload_digest: bytes,
    min_profile_generation: int,
    min_service_generation: int,
    max_total_edge_budget_units: int,
    previous_seen_capsule_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> ProfileEdgeReport:
    capsule_t = tuple(capsules)
    mode = LiveAdapterMode(expected_mode)
    component_digests = (_component_digest(live_adapter_report), _component_digest(backpressure_report), _component_digest(router_canary_report), _component_digest(ingress_drain_report), _component_digest(profile_budget_report), _component_digest(negative_scan_report))
    common = dict(mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, public_payload_digest=expected_public_payload_digest, capsules=capsule_t, components=component_digests)
    if not capsule_t:
        return _report(ProfileEdgeDecisionKind.EMPTY_NO_CAPSULES, False, False, "profile edge needs capsules", **common)
    holds = (
        (live_adapter_report, ProfileEdgeDecisionKind.HOLD_LIVE_ADAPTER),
        (backpressure_report, ProfileEdgeDecisionKind.HOLD_BACKPRESSURE),
        (profile_budget_report, ProfileEdgeDecisionKind.HOLD_PROFILE_BUDGET),
        (negative_scan_report, ProfileEdgeDecisionKind.HOLD_NEGATIVE_SCAN),
    )
    for component, hold in holds:
        if not _component_accept(component) or _component_quarantined(component):
            return _report(hold if not _component_quarantined(component) else ProfileEdgeDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "profile edge requires accepted component reports", **common)
    if mode in (LiveAdapterMode.OUTBOUND_PUBLIC_SEND, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) and (not _component_accept(router_canary_report) or _component_quarantined(router_canary_report)):
        return _report(ProfileEdgeDecisionKind.HOLD_ROUTER_CANARY if not _component_quarantined(router_canary_report) else ProfileEdgeDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "profile edge requires router canary for outbound work", **common)
    if mode in (LiveAdapterMode.INBOUND_HANDLER_WORK, LiveAdapterMode.BIDIRECTIONAL_BRIDGE_TICK) and (not _component_accept(ingress_drain_report) or _component_quarantined(ingress_drain_report)):
        return _report(ProfileEdgeDecisionKind.HOLD_INGRESS_DRAIN if not _component_quarantined(ingress_drain_report) else ProfileEdgeDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "profile edge requires ingress drain for inbound work", **common)
    if any(_component_watch(component) for component in (live_adapter_report, backpressure_report, router_canary_report, ingress_drain_report, profile_budget_report, negative_scan_report)) and not allow_component_watch:
        return _report(ProfileEdgeDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried explicitly", **common)

    seen = set(previous_seen_capsule_digests)
    by_sequence: dict[int, ProfileEdgeCapsule] = {}
    for capsule in capsule_t:
        if not capsule.verifies():
            return _report(ProfileEdgeDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad profile-edge signature", **common)
        if not capsule.live(now):
            return _report(ProfileEdgeDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future profile-edge capsule", **common)
        if capsule.capsule_digest in seen:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_REPLAY, False, False, "profile-edge capsule replayed", **common)
        if highest_seen_sequence is not None and capsule.sequence < highest_seen_sequence:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "profile-edge sequence rollback", **common)
        prior = by_sequence.get(capsule.sequence)
        if prior is not None and prior.capsule_core_digest != capsule.capsule_core_digest:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence profile-edge fork", **common)
        by_sequence[capsule.sequence] = capsule
        if capsule.profile_id != expected_profile_id:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if capsule.service_name != expected_service_name:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if capsule.mode != mode:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_MODE_DRIFT, False, False, "mode drift", **common)
        if capsule.scope_digest != expected_scope_digest:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if capsule.request_digest != expected_request_digest:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if capsule.public_payload_digest != expected_public_payload_digest:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", **common)
        if (capsule.live_adapter_digest, capsule.backpressure_digest, capsule.router_canary_digest, capsule.ingress_drain_digest, capsule.profile_budget_digest, capsule.negative_scan_digest) != component_digests:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
        if capsule.profile_generation < min_profile_generation or capsule.service_generation < min_service_generation:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_GENERATION_ROLLBACK, False, False, "profile/service generation rollback", **common)
        if capsule.hard_negative_count:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block profile edge", **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_capsule_digest != left.capsule_digest:
            return _report(ProfileEdgeDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "profile-edge previous-link mismatch", **common)
    total_budget = sum(item.edge_budget_units for item in ordered)
    if total_budget > max_total_edge_budget_units:
        return _report(ProfileEdgeDecisionKind.QUARANTINE_EDGE_BUDGET_EXCEEDED, False, False, "profile-edge budget exceeded", **common)
    family_count = len({capsule.family_id for capsule in ordered})
    path_count = len({capsule.path_family for capsule in ordered})
    if family_count < min_family_count:
        return _report(ProfileEdgeDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "profile edge needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(ProfileEdgeDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "profile edge needs more path diversity", **common)
    latest = ordered[-1]
    watch = any(_component_watch(component) for component in (live_adapter_report, backpressure_report, router_canary_report, ingress_drain_report, profile_budget_report, negative_scan_report))
    return _report(ProfileEdgeDecisionKind.ACCEPT_WITH_WATCH if watch else ProfileEdgeDecisionKind.ACCEPT_PROFILE_EDGE, True, watch, "profile edge accepted", accepted=latest, **common)
