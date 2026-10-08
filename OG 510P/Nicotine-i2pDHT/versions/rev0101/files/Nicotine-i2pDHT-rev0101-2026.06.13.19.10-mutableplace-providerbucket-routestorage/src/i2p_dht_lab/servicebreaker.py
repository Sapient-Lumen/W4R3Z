"""Circuit-breaker pressure for garden services.

A garden service may be healthy in one continuity window and harmful in the
next.  rev0040 introduces a tiny local circuit-breaker algebra so false service,
withdrawal, refusal-only loops, overload, and operator pause signals can stop a
service before future tickets or relay work turn convenience into damage.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SERVICE_BREAKER_DOMAIN = DOMAIN + b":service-breaker-v1:"


class ServiceBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServiceBreakerObservationKind(str, Enum):
    HEALTHY = "healthy"
    RECOVERY_SUCCESS = "recovery_success"
    USEFUL_REFUSAL = "useful_refusal"
    OVERLOAD = "overload"
    FALSE_SERVICE = "false_service"
    WITHDRAWAL = "withdrawal"
    OPERATOR_PAUSE = "operator_pause"
    HARD_NEGATIVE = "hard_negative"


class ServiceBreakerDecisionKind(str, Enum):
    ACCEPT_CLOSED = "accept_closed"
    ACCEPT_HALF_OPEN_PROBE = "accept_half_open_probe"
    HOLD_DEGRADED_WATCH = "hold_degraded_watch"
    HOLD_OPEN_COOLDOWN = "hold_open_cooldown"
    TRIP_OPEN_FALSE_SERVICE = "trip_open_false_service"
    TRIP_OPEN_HARD_NEGATIVE = "trip_open_hard_negative"
    TRIP_OPEN_WITHDRAWAL = "trip_open_withdrawal"
    TRIP_OPEN_OPERATOR_PAUSE = "trip_open_operator_pause"
    TRIP_OPEN_REFUSAL_LOOP = "trip_open_refusal_loop"
    TRIP_OPEN_FAILURE_STREAK = "trip_open_failure_streak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"


@dataclass(frozen=True)
class ServiceBreakerObservation:
    kind: ServiceBreakerObservationKind
    service_name: str
    scope_digest: bytes
    observation_digest: bytes
    family_id: str
    issued_at: int
    expires_at: int
    request_digest: bytes | None = None
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.family_id or len(self.family_id.encode("utf-8")) > 80:
            raise ValueError("family_id must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("observation_digest", self.observation_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.request_digest is not None and len(self.request_digest) != 32:
            raise ValueError("request_digest must be 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("breaker observation expires_at must be after issued_at")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @property
    def positive(self) -> bool:
        return self.kind in {ServiceBreakerObservationKind.HEALTHY, ServiceBreakerObservationKind.RECOVERY_SUCCESS}

    @property
    def failure(self) -> bool:
        return self.kind in {ServiceBreakerObservationKind.OVERLOAD, ServiceBreakerObservationKind.FALSE_SERVICE, ServiceBreakerObservationKind.HARD_NEGATIVE}

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"digest": self.observation_digest,
            b"family": self.family_id,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"request": self.request_digest or b"",
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class ServiceBreakerPolicy:
    min_positive_families: int = 2
    min_recovery_successes: int = 2
    max_refusal_streak: int = 2
    max_failure_streak: int = 2
    cooldown_until: int | None = None


@dataclass(frozen=True)
class ServiceBreakerReport:
    decision_kind: ServiceBreakerDecisionKind
    state: ServiceBreakerState
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    families: tuple[str, ...]
    positive_count: int
    refusal_streak: int
    failure_streak: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def open(self) -> bool:
        return self.state is ServiceBreakerState.OPEN

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceBreakerDecisionKind, state: ServiceBreakerState, accept: bool, reason: str, observations: Iterable[ServiceBreakerObservation], pressures: Iterable[bytes] = ()) -> ServiceBreakerReport:
    obs = tuple(sorted(observations, key=lambda item: item.observation_digest))
    families = tuple(sorted({item.family_id for item in obs}))
    positive = sum(1 for item in obs if item.positive)
    refusal_streak = 0
    failure_streak = 0
    for item in sorted(obs, key=lambda item: item.issued_at, reverse=True):
        if item.kind is ServiceBreakerObservationKind.USEFUL_REFUSAL:
            refusal_streak += 1
        else:
            break
    for item in sorted(obs, key=lambda item: item.issued_at, reverse=True):
        if item.failure:
            failure_streak += 1
        else:
            break
    pressure_tuple = tuple(sorted(set(pressures) | {p for item in obs for p in item.pressure_digests}))
    service = obs[0].service_name if obs else None
    scope = obs[0].scope_digest if obs else None
    digest = sha256(SERVICE_BREAKER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"state": state.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": service or "",
        b"scope": scope or b"",
        b"families": list(families),
        b"positive": positive,
        b"refusal_streak": refusal_streak,
        b"failure_streak": failure_streak,
        b"pressures": list(pressure_tuple),
    }))
    return ServiceBreakerReport(kind, state, accept, reason, service, scope, families, positive, refusal_streak, failure_streak, pressure_tuple, digest)


def assess_service_breaker(
    observations: Iterable[ServiceBreakerObservation],
    *,
    policy: ServiceBreakerPolicy | None = None,
    prior_state: ServiceBreakerState = ServiceBreakerState.CLOSED,
    now: int,
    expected_service_name: str | None = None,
    expected_scope_digest: bytes | None = None,
    previously_seen_observations: Iterable[bytes] = (),
) -> ServiceBreakerReport:
    policy = policy or ServiceBreakerPolicy()
    obs = tuple(sorted(observations, key=lambda item: (item.issued_at, item.observation_digest)))
    if not obs:
        if prior_state is ServiceBreakerState.OPEN and policy.cooldown_until and now < policy.cooldown_until:
            return _report(ServiceBreakerDecisionKind.HOLD_OPEN_COOLDOWN, ServiceBreakerState.OPEN, False, "breaker is still cooling down", obs)
        return _report(ServiceBreakerDecisionKind.HOLD_DEGRADED_WATCH, prior_state, False, "no breaker observations", obs)
    seen = set(previously_seen_observations)
    if any(item.observation_digest in seen for item in obs):
        return _report(ServiceBreakerDecisionKind.QUARANTINE_REPLAY, ServiceBreakerState.OPEN, False, "breaker observation replayed", obs)
    if any(item.issued_at > now or item.expires_at <= now for item in obs):
        return _report(ServiceBreakerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, ServiceBreakerState.OPEN, False, "breaker observation outside local time window", obs)
    if expected_service_name and any(item.service_name != expected_service_name for item in obs):
        return _report(ServiceBreakerDecisionKind.QUARANTINE_SERVICE_DRIFT, ServiceBreakerState.OPEN, False, "breaker service drift", obs)
    if expected_scope_digest and any(item.scope_digest != expected_scope_digest for item in obs):
        return _report(ServiceBreakerDecisionKind.QUARANTINE_SCOPE_DRIFT, ServiceBreakerState.OPEN, False, "breaker scope drift", obs)
    if any(item.kind is ServiceBreakerObservationKind.FALSE_SERVICE for item in obs):
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_FALSE_SERVICE, ServiceBreakerState.OPEN, False, "false service observed", obs)
    if any(item.kind is ServiceBreakerObservationKind.HARD_NEGATIVE for item in obs):
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_HARD_NEGATIVE, ServiceBreakerState.OPEN, False, "hard negative observed", obs)
    if any(item.kind is ServiceBreakerObservationKind.WITHDRAWAL for item in obs):
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_WITHDRAWAL, ServiceBreakerState.OPEN, False, "withdrawal observed", obs)
    if any(item.kind is ServiceBreakerObservationKind.OPERATOR_PAUSE for item in obs):
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_OPERATOR_PAUSE, ServiceBreakerState.OPEN, False, "operator pause observed", obs)
    if prior_state is ServiceBreakerState.OPEN and policy.cooldown_until and now < policy.cooldown_until:
        return _report(ServiceBreakerDecisionKind.HOLD_OPEN_COOLDOWN, ServiceBreakerState.OPEN, False, "breaker cooldown still active", obs)
    refusal_streak = 0
    failure_streak = 0
    for item in reversed(obs):
        if item.kind is ServiceBreakerObservationKind.USEFUL_REFUSAL:
            refusal_streak += 1
        else:
            break
    for item in reversed(obs):
        if item.failure:
            failure_streak += 1
        else:
            break
    if refusal_streak > policy.max_refusal_streak:
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_REFUSAL_LOOP, ServiceBreakerState.OPEN, False, "refusal-only loop tripped breaker", obs)
    if failure_streak > policy.max_failure_streak:
        return _report(ServiceBreakerDecisionKind.TRIP_OPEN_FAILURE_STREAK, ServiceBreakerState.OPEN, False, "failure streak tripped breaker", obs)
    positive = tuple(item for item in obs if item.positive)
    positive_families = {item.family_id for item in positive}
    if len(positive) >= policy.min_recovery_successes and len(positive_families) < policy.min_positive_families:
        return _report(ServiceBreakerDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, ServiceBreakerState.OPEN, False, "positive breaker evidence is one-family", obs)
    if prior_state is ServiceBreakerState.OPEN:
        if len(positive) >= policy.min_recovery_successes and len(positive_families) >= policy.min_positive_families:
            return _report(ServiceBreakerDecisionKind.ACCEPT_HALF_OPEN_PROBE, ServiceBreakerState.HALF_OPEN, True, "breaker may half-open for bounded probe", obs)
        return _report(ServiceBreakerDecisionKind.HOLD_OPEN_COOLDOWN, ServiceBreakerState.OPEN, False, "not enough diverse recovery evidence", obs)
    if prior_state is ServiceBreakerState.HALF_OPEN:
        if len(positive) >= policy.min_recovery_successes and len(positive_families) >= policy.min_positive_families:
            return _report(ServiceBreakerDecisionKind.ACCEPT_CLOSED, ServiceBreakerState.CLOSED, True, "half-open probe closed breaker", obs)
        return _report(ServiceBreakerDecisionKind.HOLD_DEGRADED_WATCH, ServiceBreakerState.HALF_OPEN, False, "half-open breaker still needs diverse success", obs)
    if len(positive) >= policy.min_recovery_successes and len(positive_families) >= policy.min_positive_families:
        return _report(ServiceBreakerDecisionKind.ACCEPT_CLOSED, ServiceBreakerState.CLOSED, True, "service breaker remains closed", obs)
    return _report(ServiceBreakerDecisionKind.HOLD_DEGRADED_WATCH, ServiceBreakerState.CLOSED, False, "service breaker needs more observations", obs)
