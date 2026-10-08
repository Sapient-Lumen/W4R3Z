"""Service health windows after joined continuity acceptance.

rev0038 made service-continuity a joined boundary.  rev0039 adds the next
risk surface: repeated health observations after that boundary.  A garden
service can look continuous once and still degrade into refusal-only service,
probe monoculture, metadata over-spend, stale observations, or hidden active
withdrawal.  This module keeps health as typed local pressure, not reputation
or remote truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SERVICE_HEALTH_DOMAIN = DOMAIN + b":service-health-v1:"


class ServiceHealthObservationKind(str, Enum):
    CONTINUITY_ACCEPTED = "continuity_accepted"
    PROBE_OK = "probe_ok"
    PROBE_FAILED = "probe_failed"
    RECEIPT_COMPLETED = "receipt_completed"
    RECEIPT_REFUSED = "receipt_refused"
    LOAD_OK = "load_ok"
    LOAD_REFUSED = "load_refused"
    WITHDRAWAL_ACTIVE = "withdrawal_active"
    HARD_NEGATIVE = "hard_negative"


class ServiceHealthDecisionKind(str, Enum):
    ACCEPT_HEALTHY_CONTINUE = "accept_healthy_continue"
    HOLD_MORE_OBSERVATIONS = "hold_more_observations"
    HOLD_DEGRADED_WATCH = "hold_degraded_watch"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_WITHDRAWAL_ACTIVE = "quarantine_withdrawal_active"
    QUARANTINE_BRANCH_REPORT = "quarantine_branch_report"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_METADATA_BUDGET = "quarantine_metadata_budget"
    QUARANTINE_REFUSAL_ONLY_LOOP = "quarantine_refusal_only_loop"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"


@dataclass(frozen=True)
class ServiceHealthObservation:
    kind: ServiceHealthObservationKind
    service_name: str
    scope_digest: bytes
    observation_digest: bytes
    family_id: str
    issued_at: int
    expires_at: int
    branch: str = "unknown"
    request_digest: bytes | None = None
    accept: bool = True
    refused_usefully: bool = False
    quarantined: bool = False
    raw_key_exposure: int = 0
    metadata_bytes: int = 0
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.family_id or len(self.family_id.encode("utf-8")) > 80:
            raise ValueError("family_id must be short and non-empty")
        if not self.branch or len(self.branch.encode("utf-8")) > 80:
            raise ValueError("branch must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("observation_digest", self.observation_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.request_digest is not None and len(self.request_digest) != 32:
            raise ValueError("request_digest must be 32 bytes when present")
        if self.expires_at <= self.issued_at:
            raise ValueError("health observation expires_at must be after issued_at")
        if self.raw_key_exposure < 0 or self.metadata_bytes < 0:
            raise ValueError("health observation budgets must be non-negative")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @property
    def positive(self) -> bool:
        return self.accept and not self.refused_usefully and not self.quarantined and self.kind not in {
            ServiceHealthObservationKind.PROBE_FAILED,
            ServiceHealthObservationKind.LOAD_REFUSED,
            ServiceHealthObservationKind.WITHDRAWAL_ACTIVE,
            ServiceHealthObservationKind.HARD_NEGATIVE,
            ServiceHealthObservationKind.RECEIPT_REFUSED,
        }

    @property
    def active_withdrawal(self) -> bool:
        return self.kind is ServiceHealthObservationKind.WITHDRAWAL_ACTIVE

    @property
    def hard_negative(self) -> bool:
        return self.kind is ServiceHealthObservationKind.HARD_NEGATIVE

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"digest": self.observation_digest,
            b"family": self.family_id,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"branch": self.branch,
            b"request": self.request_digest or b"",
            b"accept": 1 if self.accept else 0,
            b"refused": 1 if self.refused_usefully else 0,
            b"quarantined": 1 if self.quarantined else 0,
            b"raw": self.raw_key_exposure,
            b"meta": self.metadata_bytes,
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class ServiceHealthPolicy:
    required_kinds: tuple[ServiceHealthObservationKind, ...]
    min_families: int = 2
    min_positive_observations: int = 2
    max_refusal_ratio_percent: int = 50
    max_raw_key_exposure: int = 0
    max_metadata_bytes: int = 4096
    allow_hard_negative: bool = False

    def __post_init__(self) -> None:
        if not self.required_kinds:
            raise ValueError("service health needs at least one required observation kind")
        if self.min_families <= 0 or self.min_positive_observations <= 0:
            raise ValueError("service health minima must be positive")
        if self.max_refusal_ratio_percent < 0 or self.max_refusal_ratio_percent > 100:
            raise ValueError("refusal ratio must be between 0 and 100")
        if self.max_raw_key_exposure < 0 or self.max_metadata_bytes < 0:
            raise ValueError("metadata budgets must be non-negative")


@dataclass(frozen=True)
class ServiceHealthReport:
    decision_kind: ServiceHealthDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    families: tuple[str, ...]
    observation_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    raw_key_exposure: int
    metadata_bytes: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: ServiceHealthDecisionKind,
    accept: bool,
    reason: str,
    *,
    observations: Iterable[ServiceHealthObservation],
    service_name: str | None = None,
    scope_digest: bytes | None = None,
    pressures: Iterable[bytes] = (),
) -> ServiceHealthReport:
    obs = tuple(observations)
    families = tuple(sorted({o.family_id for o in obs}))
    digests = tuple(sorted({o.observation_digest for o in obs}))
    pressure_tuple = tuple(sorted(set(pressures) | {d for o in obs for d in o.pressure_digests}))
    raw = sum(o.raw_key_exposure for o in obs)
    meta = sum(o.metadata_bytes for o in obs)
    digest = sha256(SERVICE_HEALTH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": service_name or "",
        b"scope": scope_digest or b"",
        b"families": list(families),
        b"observations": list(digests),
        b"pressures": list(pressure_tuple),
        b"raw": raw,
        b"meta": meta,
    }))
    return ServiceHealthReport(kind, accept, reason, service_name, scope_digest, families, digests, pressure_tuple, raw, meta, digest)


def assess_service_health(
    observations: Iterable[ServiceHealthObservation],
    *,
    policy: ServiceHealthPolicy,
    now: int,
    expected_service: str | None = None,
    expected_scope_digest: bytes | None = None,
    previously_seen_observations: Iterable[bytes] = (),
) -> ServiceHealthReport:
    """Assess a post-continuity health window without turning it into reputation."""
    obs = tuple(observations)
    if not obs:
        return _report(ServiceHealthDecisionKind.HOLD_MORE_OBSERVATIONS, False, "no health observations supplied", observations=())

    seen = set(previously_seen_observations)
    for item in obs:
        if item.observation_digest in seen:
            return _report(ServiceHealthDecisionKind.QUARANTINE_REPLAY, False, "health observation replayed", observations=obs, pressures=(item.observation_digest,))
        if not (item.issued_at <= now < item.expires_at):
            return _report(ServiceHealthDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "health observation outside valid time window", observations=obs, pressures=(item.observation_digest,))
        if item.quarantined:
            return _report(ServiceHealthDecisionKind.QUARANTINE_BRANCH_REPORT, False, "health observation already quarantined by source lane", observations=obs, pressures=(item.observation_digest,))
        if item.active_withdrawal:
            return _report(ServiceHealthDecisionKind.QUARANTINE_WITHDRAWAL_ACTIVE, False, "active withdrawal blocks healthy continuation", observations=obs, pressures=(item.observation_digest,))
        if item.hard_negative and not policy.allow_hard_negative:
            return _report(ServiceHealthDecisionKind.QUARANTINE_HARD_NEGATIVE, False, "hard negative blocks healthy continuation", observations=obs, pressures=(item.observation_digest,))

    services = {o.service_name for o in obs}
    if expected_service is not None:
        services.add(expected_service)
    if len(services) != 1:
        return _report(ServiceHealthDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "health observations disagree on service", observations=obs)
    scopes = {o.scope_digest for o in obs}
    if expected_scope_digest is not None:
        scopes.add(expected_scope_digest)
    if len(scopes) != 1:
        return _report(ServiceHealthDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "health observations disagree on scope", observations=obs, pressures=scopes)

    families = {o.family_id for o in obs if o.accept or o.kind is ServiceHealthObservationKind.PROBE_OK}
    if len(families) < policy.min_families:
        return _report(ServiceHealthDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "too few independent health families", observations=obs)

    raw = sum(o.raw_key_exposure for o in obs)
    meta = sum(o.metadata_bytes for o in obs)
    if raw > policy.max_raw_key_exposure or meta > policy.max_metadata_bytes:
        return _report(ServiceHealthDecisionKind.QUARANTINE_METADATA_BUDGET, False, "health window exceeded metadata budget", observations=obs)

    kinds = {o.kind for o in obs}
    missing = [kind.value for kind in policy.required_kinds if kind not in kinds]
    if missing:
        return _report(ServiceHealthDecisionKind.HOLD_MORE_OBSERVATIONS, False, "missing required health observations: " + ",".join(missing), observations=obs)

    positives = sum(1 for o in obs if o.positive)
    refusals = sum(1 for o in obs if o.refused_usefully or o.kind in {ServiceHealthObservationKind.RECEIPT_REFUSED, ServiceHealthObservationKind.LOAD_REFUSED})
    if obs and refusals * 100 > len(obs) * policy.max_refusal_ratio_percent:
        return _report(ServiceHealthDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP, False, "refusal-only or refusal-heavy health loop", observations=obs)
    if positives < policy.min_positive_observations:
        return _report(ServiceHealthDecisionKind.HOLD_DEGRADED_WATCH, False, "not enough positive health observations", observations=obs)

    service = next(iter(services))
    scope = next(iter(scopes))
    return _report(ServiceHealthDecisionKind.ACCEPT_HEALTHY_CONTINUE, True, "health window is locally diverse and budgeted", observations=obs, service_name=service, scope_digest=scope)
