"""Handler quench and cooldown algebra for repeated near-miss ingress.

rev0054 models the case where inbound public-edge handler requests are not
obviously malicious one at a time, but become dangerous when repeated: almost
passing capsules, refusal-only loops, raw-key budget pressure, and low-diversity
families can burn metadata and operator attention.  The output is local pressure
only; it is not reputation and not DHT truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

HANDLER_QUENCH_DOMAIN = DOMAIN + b":handler-quench-v1:"


class HandlerQuenchDecisionKind(str, Enum):
    ALLOW_HANDLER_WINDOW = "allow_handler_window"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    COOLDOWN_ALMOST_PASSING_LOOP = "cooldown_almost_passing_loop"
    COOLDOWN_USEFUL_REFUSAL_LOOP = "cooldown_useful_refusal_loop"
    QUENCH_RAW_KEY_PRESSURE = "quench_raw_key_pressure"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_CALLER_DRIFT = "quarantine_caller_drift"
    QUARANTINE_HANDLER_DRIFT = "quarantine_handler_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"


@dataclass(frozen=True)
class HandlerAttemptObservation:
    decision: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    report_digest: bytes
    metadata_units: int
    raw_key_units: int
    useful_refusal: bool
    hard_negative_count: int
    observed_at: int
    family_id: str
    path_family: str

    def __post_init__(self) -> None:
        if not self.decision or not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("handler observation needs decision/profile/service/family/path")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("caller_digest", self.caller_digest),
            ("handler_digest", self.handler_digest),
            ("report_digest", self.report_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for name in ("metadata_units", "raw_key_units", "hard_negative_count", "observed_at"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")

    @property
    def near_miss(self) -> bool:
        return self.decision.startswith("hold_") or self.decision == "accept_with_watch" or self.decision.endswith("with_watch")

    @property
    def hard_negative(self) -> bool:
        return self.hard_negative_count > 0 or self.decision.startswith("quarantine_hard_negative")

    def bvalue(self) -> dict[bytes, object]:
        return {b"decision": self.decision, b"report": self.report_digest, b"metadata": self.metadata_units, b"raw": self.raw_key_units, b"refusal": 1 if self.useful_refusal else 0, b"hard": self.hard_negative_count, b"family": self.family_id, b"path_family": self.path_family, b"time": self.observed_at}


@dataclass(frozen=True)
class HandlerQuenchReport:
    decision_kind: HandlerQuenchDecisionKind
    accept: bool
    watch: bool
    cooldown_until: int
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    caller_digest: bytes
    handler_digest: bytes
    observation_count: int
    near_miss_count: int
    useful_refusal_count: int
    metadata_units: int
    raw_key_units: int
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_") or self.decision_kind.value.startswith("quench_")


def assess_handler_quench(
    observations: Iterable[HandlerAttemptObservation],
    *,
    now: int,
    window_seconds: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_caller_digest: bytes,
    expected_handler_digest: bytes,
    previous_seen_report_digests: Iterable[bytes] = (),
    max_near_misses: int = 3,
    max_useful_refusals: int = 4,
    max_raw_key_units: int = 1,
    cooldown_seconds: int = 120,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> HandlerQuenchReport:
    lower = max(0, now - window_seconds)
    obs = tuple(item for item in observations if lower <= item.observed_at <= now)
    common = dict(profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, caller_digest=expected_caller_digest, handler_digest=expected_handler_digest)
    if not obs:
        return _report(HandlerQuenchDecisionKind.EMPTY_NO_OBSERVATIONS, False, True, now, "handler quench needs observations", obs, **common)
    seen = set(previous_seen_report_digests)
    local_seen: set[bytes] = set()
    for item in obs:
        if item.report_digest in seen or item.report_digest in local_seen:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_REPLAY, False, False, now + cooldown_seconds, "replayed handler observation", obs, **common)
        local_seen.add(item.report_digest)
        if item.profile_id != expected_profile_id or item.service_name != expected_service_name:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, now + cooldown_seconds, "profile/service drift", obs, **common)
        if item.scope_digest != expected_scope_digest:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, now + cooldown_seconds, "scope drift", obs, **common)
        if item.request_digest != expected_request_digest:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, now + cooldown_seconds, "request drift", obs, **common)
        if item.caller_digest != expected_caller_digest:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_CALLER_DRIFT, False, False, now + cooldown_seconds, "caller drift", obs, **common)
        if item.handler_digest != expected_handler_digest:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_HANDLER_DRIFT, False, False, now + cooldown_seconds, "handler drift", obs, **common)
        if item.hard_negative:
            return _report(HandlerQuenchDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, now + cooldown_seconds, "hard negative blocks handler window", obs, **common)
    families = {item.family_id for item in obs}
    paths = {item.path_family for item in obs}
    if len(families) < min_family_count:
        return _report(HandlerQuenchDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, now + cooldown_seconds // 2, "handler window needs more family diversity", obs, **common)
    if len(paths) < min_path_family_count:
        return _report(HandlerQuenchDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, now + cooldown_seconds // 2, "handler window needs more path diversity", obs, **common)
    raw = sum(item.raw_key_units for item in obs)
    if raw > max_raw_key_units:
        return _report(HandlerQuenchDecisionKind.QUENCH_RAW_KEY_PRESSURE, False, False, now + cooldown_seconds, "raw-key metadata budget exceeded", obs, **common)
    near = sum(1 for item in obs if item.near_miss)
    if near >= max_near_misses:
        return _report(HandlerQuenchDecisionKind.COOLDOWN_ALMOST_PASSING_LOOP, False, True, now + cooldown_seconds, "almost-passing handler loop cooled down", obs, **common)
    refusals = sum(1 for item in obs if item.useful_refusal)
    if refusals >= max_useful_refusals:
        return _report(HandlerQuenchDecisionKind.COOLDOWN_USEFUL_REFUSAL_LOOP, False, True, now + cooldown_seconds, "useful-refusal loop cooled down", obs, **common)
    return _report(HandlerQuenchDecisionKind.ALLOW_HANDLER_WINDOW, True, False, now, "handler window allowed", obs, **common)


def _report(kind: HandlerQuenchDecisionKind, accept: bool, watch: bool, cooldown_until: int, reason: str, observations: tuple[HandlerAttemptObservation, ...], *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, caller_digest: bytes, handler_digest: bytes) -> HandlerQuenchReport:
    families = {item.family_id for item in observations}
    paths = {item.path_family for item in observations}
    near = sum(1 for item in observations if item.near_miss)
    refusals = sum(1 for item in observations if item.useful_refusal)
    metadata = sum(item.metadata_units for item in observations)
    raw = sum(item.raw_key_units for item in observations)
    digest = sha256(HANDLER_QUENCH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"cooldown": cooldown_until,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"caller": caller_digest,
        b"handler": handler_digest,
        b"observations": [item.bvalue() for item in observations],
        b"families": len(families),
        b"paths": len(paths),
        b"near": near,
        b"refusals": refusals,
        b"metadata": metadata,
        b"raw": raw,
    }))
    return HandlerQuenchReport(kind, accept, watch, cooldown_until, reason, profile_id, service_name, scope_digest, request_digest, caller_digest, handler_digest, len(observations), near, refusals, metadata, raw, len(families), len(paths), digest)


def observation_from_report(*, report: Any, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, caller_digest: bytes, handler_digest: bytes, observed_at: int, family_id: str, path_family: str, metadata_units: int = 0, raw_key_units: int = 0, useful_refusal: bool = False, hard_negative_count: int = 0) -> HandlerAttemptObservation:
    decision = getattr(getattr(report, "decision_kind", None), "value", str(getattr(report, "decision_kind", "unknown")))
    digest = getattr(report, "report_digest", ZERO_DIGEST)
    if not isinstance(digest, bytes) or len(digest) != 32:
        digest = sha256(decision.encode("utf-8"))
    return HandlerAttemptObservation(decision, profile_id, service_name, scope_digest, request_digest, caller_digest, handler_digest, digest, metadata_units, raw_key_units, useful_refusal, hard_negative_count, observed_at, family_id, path_family)
