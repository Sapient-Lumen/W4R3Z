"""Repeated service-probe loop pressure.

A service probe is valuable because it checks whether a garden service is really
there. It is dangerous because it can leak interest, create a cheap oracle, or
turn useful refusals into fake health. rev0039 keeps repeated probe windows as
local observations that need metadata budget, family diversity, and at least one
positive non-refusal signal before they advance service health memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

PROBE_LOOP_DOMAIN = DOMAIN + b":probe-loop-v1:"


class ProbeLoopObservationKind(str, Enum):
    HEALTHY = "healthy"
    USEFUL_REFUSAL = "useful_refusal"
    OVERLOADED = "overloaded"
    TIMEOUT = "timeout"
    FALSE_SERVICE = "false_service"


class ProbeLoopDecisionKind(str, Enum):
    ACCEPT_PROBE_LOOP_HEALTH = "accept_probe_loop_health"
    HOLD_INSUFFICIENT_HEALTH = "hold_insufficient_health"
    HOLD_REFUSAL_ONLY = "hold_refusal_only"
    HOLD_OVERLOADED = "hold_overloaded"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_RAW_KEY_BUDGET = "quarantine_raw_key_budget"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_FALSE_SERVICE = "quarantine_false_service"
    QUARANTINE_DECOY_SHORTFALL = "quarantine_decoy_shortfall"


@dataclass(frozen=True)
class ProbeLoopPolicy:
    min_healthy: int = 2
    min_source_families: int = 2
    min_path_families: int = 2
    max_raw_key_exposures: int = 1
    min_decoy_count: int = 1
    max_family_share: float = 0.67

    def __post_init__(self) -> None:
        if self.min_healthy < 0 or self.min_source_families <= 0 or self.min_path_families <= 0:
            raise ValueError("probe loop diversity thresholds must be positive")
        if self.max_raw_key_exposures < 0 or self.min_decoy_count < 0:
            raise ValueError("probe loop metadata counters must be non-negative")
        if not (0 < self.max_family_share <= 1):
            raise ValueError("max_family_share must be in (0, 1]")


@dataclass(frozen=True)
class ProbeLoopObservation:
    receipt_digest: bytes
    plan_digest: bytes
    service_name: str
    kind: ProbeLoopObservationKind
    source_family: str
    path_family: str
    raw_key_exposures: int = 0
    decoy_count: int = 0
    latency_ms: int = 0
    retry_after_seconds: int = 0

    def __post_init__(self) -> None:
        for name, value in (("receipt_digest", self.receipt_digest), ("plan_digest", self.plan_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.source_family or not self.path_family:
            raise ValueError("probe loop observations need family hints")
        if self.raw_key_exposures < 0 or self.decoy_count < 0 or self.latency_ms < 0 or self.retry_after_seconds < 0:
            raise ValueError("probe loop counters must be non-negative")

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"receipt_digest": self.receipt_digest,
            b"plan_digest": self.plan_digest,
            b"service_name": self.service_name,
            b"kind": self.kind.value,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"raw_key_exposures": self.raw_key_exposures,
            b"decoy_count": self.decoy_count,
            b"latency_ms": self.latency_ms,
            b"retry_after_seconds": self.retry_after_seconds,
        }


@dataclass(frozen=True)
class ProbeLoopReport:
    decision_kind: ProbeLoopDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    healthy_count: int
    source_family_count: int
    path_family_count: int
    raw_key_exposures: int
    decoy_count: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ProbeLoopDecisionKind, accept: bool, reason: str, *, observations: Iterable[ProbeLoopObservation], pressures: Iterable[bytes] = ()) -> ProbeLoopReport:
    obs = tuple(observations)
    services = {item.service_name for item in obs}
    service_name = next(iter(services)) if len(services) == 1 else None
    healthy = sum(1 for item in obs if item.kind is ProbeLoopObservationKind.HEALTHY)
    src = {item.source_family for item in obs}
    path = {item.path_family for item in obs}
    raw = sum(item.raw_key_exposures for item in obs)
    decoy = sum(item.decoy_count for item in obs)
    pressure_tuple = tuple(sorted(set(pressures)))
    digest = sha256(PROBE_LOOP_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service_name": service_name or "",
        b"healthy_count": healthy,
        b"source_family_count": len(src),
        b"path_family_count": len(path),
        b"raw_key_exposures": raw,
        b"decoy_count": decoy,
        b"pressures": list(pressure_tuple),
    }))
    return ProbeLoopReport(kind, accept, reason, service_name, healthy, len(src), len(path), raw, decoy, pressure_tuple, digest)


def _family_monoculture(families: list[str], max_share: float) -> bool:
    if not families:
        return False
    counts: dict[str, int] = {}
    for family in families:
        counts[family] = counts.get(family, 0) + 1
    return max(counts.values()) > 1 and (max(counts.values()) / len(families)) >= (max_share - 0.01)


def assess_probe_loop(observations: Iterable[ProbeLoopObservation], *, policy: ProbeLoopPolicy, previously_seen_receipts: Iterable[bytes] = ()) -> ProbeLoopReport:
    obs = tuple(observations)
    if not obs:
        return _report(ProbeLoopDecisionKind.HOLD_INSUFFICIENT_HEALTH, False, "no probe-loop observations supplied", observations=())
    seen = set(previously_seen_receipts)
    local_seen: set[bytes] = set()
    for item in obs:
        if item.receipt_digest in seen or item.receipt_digest in local_seen:
            return _report(ProbeLoopDecisionKind.QUARANTINE_REPLAY, False, "probe receipt replayed", observations=obs, pressures=(item.receipt_digest,))
        local_seen.add(item.receipt_digest)
    raw = sum(item.raw_key_exposures for item in obs)
    if raw > policy.max_raw_key_exposures:
        return _report(ProbeLoopDecisionKind.QUARANTINE_RAW_KEY_BUDGET, False, "probe loop exceeded raw-key exposure budget", observations=obs, pressures=(obs[0].plan_digest,))
    decoys = sum(item.decoy_count for item in obs)
    if raw and decoys < policy.min_decoy_count:
        return _report(ProbeLoopDecisionKind.QUARANTINE_DECOY_SHORTFALL, False, "raw-key probe had too little cover", observations=obs, pressures=(obs[0].plan_digest,))
    if _family_monoculture([item.source_family for item in obs], policy.max_family_share) or _family_monoculture([item.path_family for item in obs], policy.max_family_share):
        return _report(ProbeLoopDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "probe loop dominated by one family", observations=obs, pressures=(item.receipt_digest for item in obs))
    if any(item.kind is ProbeLoopObservationKind.FALSE_SERVICE for item in obs):
        return _report(ProbeLoopDecisionKind.QUARANTINE_FALSE_SERVICE, False, "service probe observed false service behavior", observations=obs, pressures=(item.receipt_digest for item in obs if item.kind is ProbeLoopObservationKind.FALSE_SERVICE))
    if all(item.kind is ProbeLoopObservationKind.USEFUL_REFUSAL for item in obs):
        return _report(ProbeLoopDecisionKind.HOLD_REFUSAL_ONLY, False, "only useful refusals observed", observations=obs)
    if all(item.kind in {ProbeLoopObservationKind.USEFUL_REFUSAL, ProbeLoopObservationKind.OVERLOADED, ProbeLoopObservationKind.TIMEOUT} for item in obs):
        return _report(ProbeLoopDecisionKind.HOLD_OVERLOADED, False, "probe loop did not produce positive health", observations=obs)
    healthy = sum(1 for item in obs if item.kind is ProbeLoopObservationKind.HEALTHY)
    if healthy < policy.min_healthy:
        return _report(ProbeLoopDecisionKind.HOLD_INSUFFICIENT_HEALTH, False, "probe loop has too few healthy observations", observations=obs)
    if len({item.source_family for item in obs if item.kind is ProbeLoopObservationKind.HEALTHY}) < policy.min_source_families or len({item.path_family for item in obs if item.kind is ProbeLoopObservationKind.HEALTHY}) < policy.min_path_families:
        return _report(ProbeLoopDecisionKind.HOLD_INSUFFICIENT_HEALTH, False, "healthy observations lack family diversity", observations=obs)
    return _report(ProbeLoopDecisionKind.ACCEPT_PROBE_LOOP_HEALTH, True, "probe loop accepted with diverse positive health", observations=obs)
