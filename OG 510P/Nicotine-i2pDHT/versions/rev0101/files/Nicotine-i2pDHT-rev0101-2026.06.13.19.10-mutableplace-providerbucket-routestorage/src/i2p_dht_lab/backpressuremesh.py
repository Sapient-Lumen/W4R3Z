"""Shared public-edge backpressure mesh.

rev0051 made outbound router/session canaries and inbound ingress drains
separate no-network boundaries.  rev0052 adds the shared pressure surface that
sits between them: a garden bridge cannot spend inbound handler work, outbound
publication work, router slots, and metadata budget as if each lane were alone.

This is intentionally still a deterministic toy surface.  It does not schedule
real sockets or handler work.  It makes the dangerous guess executable: inbound
and outbound budgets must be joined before any future live adapter can run.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

BACKPRESSURE_DOMAIN = DOMAIN + b":backpressure-mesh-v1:"


class BackpressureMode(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    BIDIRECTIONAL = "bidirectional"


class BackpressureDecisionKind(str, Enum):
    ACCEPT_BACKPRESSURE = "accept_backpressure"
    ACCEPT_WITH_SHED_BULK = "accept_with_shed_bulk"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_ROUTER_CANARY = "hold_router_canary"
    HOLD_INGRESS_DRAIN = "hold_ingress_drain"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_MODE_DRIFT = "quarantine_mode_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_TOTAL_BUDGET = "quarantine_total_budget"
    QUARANTINE_METADATA_BUDGET = "quarantine_metadata_budget"
    QUARANTINE_REFUSAL_LOOP = "quarantine_refusal_loop"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_PROTECTED_RESERVE_STARVED = "quarantine_protected_reserve_starved"


@dataclass(frozen=True)
class BackpressureObservation:
    mode: BackpressureMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    router_canary_digest: bytes
    ingress_drain_digest: bytes
    inbound_units: int
    outbound_units: int
    router_units: int
    protected_reserve_units: int
    raw_key_units: int
    useful_refusal_streak: int
    hard_negative_count: int
    sequence: int
    previous_observation_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", BackpressureMode(self.mode))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("backpressure observation needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name in ("inbound_units", "outbound_units", "router_units", "protected_reserve_units", "raw_key_units", "useful_refusal_streak", "hard_negative_count"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("router_canary_digest", self.router_canary_digest),
            ("ingress_drain_digest", self.ingress_drain_digest),
            ("previous_observation_digest", self.previous_observation_digest),
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
            b"router": self.router_canary_digest,
            b"ingress": self.ingress_drain_digest,
            b"inbound": self.inbound_units,
            b"outbound": self.outbound_units,
            b"router_units": self.router_units,
            b"reserve": self.protected_reserve_units,
            b"raw_key": self.raw_key_units,
            b"refusal_streak": self.useful_refusal_streak,
            b"hard_negatives": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_observation_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return BACKPRESSURE_DOMAIN + b":observation-sig:" + bencode(self.unsigned_bvalue())

    @property
    def observation_core_digest(self) -> bytes:
        return sha256(BACKPRESSURE_DOMAIN + b":observation-core:" + bencode(self.unsigned_bvalue()))

    @property
    def observation_digest(self) -> bytes:
        return sha256(BACKPRESSURE_DOMAIN + b":observation-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class BackpressureReport:
    decision_kind: BackpressureDecisionKind
    accept: bool
    watch: bool
    shed_bulk: bool
    reason: str
    mode: BackpressureMode
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    total_units: int
    raw_key_units: int
    useful_refusal_streak: int
    hard_negative_count: int
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


def make_backpressure_observation(
    *,
    keypair: DhtKeypair,
    mode: BackpressureMode,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    router_canary_report: Any,
    ingress_drain_report: Any,
    inbound_units: int,
    outbound_units: int,
    router_units: int,
    protected_reserve_units: int,
    raw_key_units: int,
    useful_refusal_streak: int,
    hard_negative_count: int,
    sequence: int,
    previous_observation_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> BackpressureObservation:
    unsigned = BackpressureObservation(
        mode=mode,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        router_canary_digest=_component_digest(router_canary_report),
        ingress_drain_digest=_component_digest(ingress_drain_report),
        inbound_units=inbound_units,
        outbound_units=outbound_units,
        router_units=router_units,
        protected_reserve_units=protected_reserve_units,
        raw_key_units=raw_key_units,
        useful_refusal_streak=useful_refusal_streak,
        hard_negative_count=hard_negative_count,
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
    kind: BackpressureDecisionKind,
    accept: bool,
    watch: bool,
    shed_bulk: bool,
    reason: str,
    *,
    mode: BackpressureMode,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    accepted: BackpressureObservation | None = None,
    observations: Iterable[BackpressureObservation] = (),
    components: Iterable[bytes] = (),
) -> BackpressureReport:
    obs = tuple(observations)
    digests = tuple(item.observation_digest for item in obs)
    families = {item.family_id for item in obs}
    paths = {item.path_family for item in obs}
    total_units = sum(item.inbound_units + item.outbound_units + item.router_units for item in obs)
    raw_key_units = sum(item.raw_key_units for item in obs)
    refusal_streak = max((item.useful_refusal_streak for item in obs), default=0)
    hard_negatives = sum(item.hard_negative_count for item in obs)
    highest = max((item.sequence for item in obs), default=-1)
    component_t = tuple(components)
    accepted_digest = accepted.observation_digest if accepted else ZERO_DIGEST
    digest = sha256(BACKPRESSURE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"shed": 1 if shed_bulk else 0,
        b"reason": reason,
        b"mode": mode.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"accepted": accepted_digest,
        b"observations": list(digests),
        b"components": list(component_t),
        b"total_units": total_units,
        b"raw_key_units": raw_key_units,
        b"refusal_streak": refusal_streak,
        b"hard_negatives": hard_negatives,
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
    }))
    return BackpressureReport(kind, accept, watch, shed_bulk, reason, mode, profile_id, service_name, scope_digest, request_digest, accepted_digest, digests, component_t, total_units, raw_key_units, refusal_streak, hard_negatives, len(families), len(paths), highest, digest)


def assess_backpressure_mesh(
    observations: Iterable[BackpressureObservation],
    *,
    router_canary_report: Any,
    ingress_drain_report: Any,
    now: int,
    expected_mode: BackpressureMode,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    max_total_units: int,
    max_raw_key_units: int,
    protected_reserve_floor: int,
    max_refusal_streak: int = 2,
    previous_seen_observation_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> BackpressureReport:
    obs = tuple(observations)
    mode = BackpressureMode(expected_mode)
    component_digests = (_component_digest(router_canary_report), _component_digest(ingress_drain_report))
    common = dict(mode=mode, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, observations=obs, components=component_digests)
    if not obs:
        return _report(BackpressureDecisionKind.EMPTY_NO_OBSERVATIONS, False, False, False, "backpressure mesh needs observations", **common)
    if mode in (BackpressureMode.OUTBOUND, BackpressureMode.BIDIRECTIONAL) and (not _component_accept(router_canary_report) or _component_quarantined(router_canary_report)):
        return _report(BackpressureDecisionKind.HOLD_ROUTER_CANARY if not _component_quarantined(router_canary_report) else BackpressureDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, False, "router canary must accept before outbound pressure", **common)
    if mode in (BackpressureMode.INBOUND, BackpressureMode.BIDIRECTIONAL) and (not _component_accept(ingress_drain_report) or _component_quarantined(ingress_drain_report)):
        return _report(BackpressureDecisionKind.HOLD_INGRESS_DRAIN if not _component_quarantined(ingress_drain_report) else BackpressureDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, False, "ingress drain must accept before inbound pressure", **common)
    if any(_component_watch(component) for component in (router_canary_report, ingress_drain_report)) and not allow_component_watch:
        return _report(BackpressureDecisionKind.HOLD_COMPONENT_WATCH, False, True, False, "component watch pressure must be carried explicitly", **common)

    seen = set(previous_seen_observation_digests)
    by_sequence: dict[int, BackpressureObservation] = {}
    for item in obs:
        if not item.verifies():
            return _report(BackpressureDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, False, "bad backpressure signature", **common)
        if not item.live(now):
            return _report(BackpressureDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, False, "expired or future backpressure observation", **common)
        if item.observation_digest in seen:
            return _report(BackpressureDecisionKind.QUARANTINE_REPLAY, False, False, False, "replayed backpressure observation", **common)
        if highest_seen_sequence is not None and item.sequence < highest_seen_sequence:
            return _report(BackpressureDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, "backpressure sequence rollback", **common)
        prior = by_sequence.get(item.sequence)
        if prior is not None and prior.observation_core_digest != item.observation_core_digest:
            return _report(BackpressureDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence backpressure fork", **common)
        by_sequence[item.sequence] = item
        if item.profile_id != expected_profile_id:
            return _report(BackpressureDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, False, "profile drift", **common)
        if item.service_name != expected_service_name:
            return _report(BackpressureDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, False, "service drift", **common)
        if item.scope_digest != expected_scope_digest:
            return _report(BackpressureDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, False, "scope drift", **common)
        if item.request_digest != expected_request_digest:
            return _report(BackpressureDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, False, "request drift", **common)
        if item.mode != mode:
            return _report(BackpressureDecisionKind.QUARANTINE_MODE_DRIFT, False, False, False, "mode drift", **common)
        if item.router_canary_digest != component_digests[0] or item.ingress_drain_digest != component_digests[1]:
            return _report(BackpressureDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, False, "component digest drift", **common)
        if item.protected_reserve_units < protected_reserve_floor:
            return _report(BackpressureDecisionKind.QUARANTINE_PROTECTED_RESERVE_STARVED, False, False, False, "protected reserve was starved", **common)
        if item.hard_negative_count:
            return _report(BackpressureDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard negative pressure blocks edge work", **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_observation_digest != left.observation_digest:
            return _report(BackpressureDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "backpressure previous-link mismatch", **common)
    total_units = sum(item.inbound_units + item.outbound_units + item.router_units for item in ordered)
    raw_key_units = sum(item.raw_key_units for item in ordered)
    refusal_streak = max(item.useful_refusal_streak for item in ordered)
    if total_units > max_total_units:
        return _report(BackpressureDecisionKind.QUARANTINE_TOTAL_BUDGET, False, False, False, "shared edge budget exceeded", **common)
    if raw_key_units > max_raw_key_units:
        return _report(BackpressureDecisionKind.QUARANTINE_METADATA_BUDGET, False, False, False, "raw-key metadata budget exceeded", **common)
    if refusal_streak > max_refusal_streak:
        return _report(BackpressureDecisionKind.QUARANTINE_REFUSAL_LOOP, False, False, False, "refusal-only pressure loop", **common)
    family_count = len({item.family_id for item in ordered})
    path_count = len({item.path_family for item in ordered})
    if family_count < min_family_count:
        return _report(BackpressureDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "backpressure needs more family diversity", **common)
    if path_count < min_path_family_count:
        return _report(BackpressureDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "backpressure needs more path diversity", **common)
    latest = ordered[-1]
    shed_bulk = total_units > max_total_units * 3 // 4 or refusal_streak > 0
    component_watch = any(_component_watch(component) for component in (router_canary_report, ingress_drain_report))
    if shed_bulk:
        return _report(BackpressureDecisionKind.ACCEPT_WITH_SHED_BULK, True, True, True, "backpressure accepted but bulk should be shed", accepted=latest, **common)
    return _report(BackpressureDecisionKind.ACCEPT_WITH_WATCH if component_watch else BackpressureDecisionKind.ACCEPT_BACKPRESSURE, True, component_watch, False, "backpressure accepted", accepted=latest, **common)
