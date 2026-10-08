"""Keyspace cartography and scout planning.

A DHT over I2P can look healthy while its local view is actually a fast,
convenient monoculture.  This module maps tiny XOR-prefix regions from local
observations and chooses bounded scout work for holes, stale regions, and
family-captured regions.

This is not a global map and not a routing oracle.  It is local cartography: a
node's own memory of which parts of keyspace it has recently seen through which
families and introducers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .sweep import key_region

KEYSPACE_CARTOGRAPHY_DOMAIN = DOMAIN + b":keyspace-cartography-v1:"


class CartographyDecisionKind(str, Enum):
    ACCEPT_COVERAGE = "accept_coverage"
    SCOUT_HOLES = "scout_holes"
    SCOUT_MONOCULTURE = "scout_monoculture"
    PRUNE_STALE_THEN_SCOUT = "prune_stale_then_scout"
    EMPTY = "empty"


class ScoutReason(str, Enum):
    HOLE = "hole"
    MONOCULTURE = "monoculture"
    STALE = "stale"
    LOW_FAMILY_DIVERSITY = "low_family_diversity"


@dataclass(frozen=True)
class RegionObservation:
    key: bytes
    family_id: str
    introducer_family: str
    observed_at: int
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0

    def __post_init__(self) -> None:
        if len(self.key) != 32:
            raise ValueError("observed key must be 32 bytes")
        if not self.family_id or not self.introducer_family:
            raise ValueError("family and introducer family are required")
        if self.success_count < 0 or self.failure_count < 0 or self.timeout_count < 0:
            raise ValueError("observation counters cannot be negative")

    @property
    def score(self) -> int:
        return self.success_count * 8 - self.failure_count * 4 - self.timeout_count

    def region(self, *, prefix_bits: int) -> int:
        return key_region(self.key, prefix_bits=prefix_bits)

    def stale(self, *, now: int, stale_after_seconds: int) -> bool:
        return now - self.observed_at > stale_after_seconds

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"key": self.key,
            b"family_id": self.family_id,
            b"introducer_family": self.introducer_family,
            b"observed_at": self.observed_at,
            b"success_count": self.success_count,
            b"failure_count": self.failure_count,
            b"timeout_count": self.timeout_count,
        }


@dataclass(frozen=True)
class CartographyPolicy:
    prefix_bits: int = 4
    min_covered_regions: int = 6
    min_families_per_region: int = 2
    max_family_fraction: float = 0.75
    stale_after_seconds: int = 72 * 3600
    scout_limit: int = 8

    def validate(self) -> None:
        if not 1 <= self.prefix_bits <= 16:
            raise ValueError("prefix_bits must be in [1, 16] for the lab")
        if self.min_covered_regions <= 0 or self.min_families_per_region <= 0 or self.scout_limit <= 0:
            raise ValueError("coverage thresholds must be positive")
        if not 0.0 < self.max_family_fraction <= 1.0:
            raise ValueError("max_family_fraction must be in (0, 1]")
        if self.stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be positive")


@dataclass(frozen=True)
class RegionSummary:
    region: int
    fresh_count: int
    stale_count: int
    family_counts: dict[str, int]
    introducer_counts: dict[str, int]
    score: int

    @property
    def family_count(self) -> int:
        return len(self.family_counts)

    @property
    def dominant_family_fraction(self) -> float:
        total = sum(self.family_counts.values())
        return max(self.family_counts.values()) / total if total else 0.0

    @property
    def introducer_monoculture(self) -> bool:
        total = sum(self.introducer_counts.values())
        return bool(total and max(self.introducer_counts.values()) == total and total > 1)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"region": self.region,
            b"fresh_count": self.fresh_count,
            b"stale_count": self.stale_count,
            b"family_counts": {k: v for k, v in sorted(self.family_counts.items())},
            b"introducer_counts": {k: v for k, v in sorted(self.introducer_counts.items())},
            b"score": self.score,
        }


@dataclass(frozen=True)
class ScoutAction:
    region: int
    reason: ScoutReason
    family_hint: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"region": self.region, b"reason": self.reason.value, b"family_hint": self.family_hint}


@dataclass(frozen=True)
class CartographyDecision:
    kind: CartographyDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class CartographyReport:
    summaries: tuple[RegionSummary, ...]
    scouts: tuple[ScoutAction, ...]
    stale_pruned: int
    decision: CartographyDecision
    transcript_digest: bytes

    @property
    def covered_regions(self) -> int:
        return sum(1 for item in self.summaries if item.fresh_count > 0)

    @property
    def needs_scouts(self) -> bool:
        return bool(self.scouts)


@dataclass
class KeyspaceCartographyBook:
    observations: dict[tuple[int, str, str, bytes], RegionObservation] = field(default_factory=dict)

    def observe(self, observation: RegionObservation, *, policy: CartographyPolicy | None = None) -> None:
        policy = policy or CartographyPolicy()
        policy.validate()
        key = (observation.region(prefix_bits=policy.prefix_bits), observation.family_id, observation.introducer_family, observation.key)
        existing = self.observations.get(key)
        if existing is None or (observation.observed_at, observation.score) >= (existing.observed_at, existing.score):
            self.observations[key] = observation

    def ingest(self, observations: Iterable[RegionObservation], *, policy: CartographyPolicy | None = None) -> int:
        count = 0
        for observation in observations:
            self.observe(observation, policy=policy)
            count += 1
        return count

    def prune_stale(self, *, now: int, policy: CartographyPolicy | None = None) -> int:
        policy = policy or CartographyPolicy()
        policy.validate()
        removed = 0
        for key, observation in list(self.observations.items()):
            if observation.stale(now=now, stale_after_seconds=policy.stale_after_seconds):
                del self.observations[key]
                removed += 1
        return removed

    def analyze(self, *, now: int, policy: CartographyPolicy | None = None, prune_stale: bool = False) -> CartographyReport:
        policy = policy or CartographyPolicy()
        policy.validate()
        stale_pruned = self.prune_stale(now=now, policy=policy) if prune_stale else 0
        region_count = 1 << policy.prefix_bits
        fresh_by_region: dict[int, list[RegionObservation]] = {idx: [] for idx in range(region_count)}
        stale_by_region: dict[int, list[RegionObservation]] = {idx: [] for idx in range(region_count)}
        for observation in self.observations.values():
            region = observation.region(prefix_bits=policy.prefix_bits)
            if observation.stale(now=now, stale_after_seconds=policy.stale_after_seconds):
                stale_by_region[region].append(observation)
            else:
                fresh_by_region[region].append(observation)

        summaries: list[RegionSummary] = []
        for region in range(region_count):
            family_counts: dict[str, int] = {}
            introducer_counts: dict[str, int] = {}
            score = 0
            for observation in fresh_by_region[region]:
                family_counts[observation.family_id] = family_counts.get(observation.family_id, 0) + 1
                introducer_counts[observation.introducer_family] = introducer_counts.get(observation.introducer_family, 0) + 1
                score += observation.score
            summaries.append(RegionSummary(region, len(fresh_by_region[region]), len(stale_by_region[region]), family_counts, introducer_counts, score))

        holes = [item for item in summaries if item.fresh_count == 0]
        stale_regions = [item for item in summaries if item.fresh_count == 0 and item.stale_count > 0]
        low_diversity = [item for item in summaries if item.fresh_count > 0 and item.family_count < policy.min_families_per_region]
        monoculture = [item for item in summaries if item.fresh_count >= policy.min_families_per_region and item.dominant_family_fraction > policy.max_family_fraction]
        introducer_capture = [item for item in summaries if item.fresh_count > 1 and item.introducer_monoculture]

        scouts: list[ScoutAction] = []
        for item in stale_regions:
            scouts.append(ScoutAction(item.region, ScoutReason.STALE))
        # Capture-looking regions are more urgent than ordinary holes: a hole is
        # absence, while monoculture is potentially misleading presence.
        for item in monoculture + introducer_capture:
            hint = max(item.family_counts, key=item.family_counts.get) if item.family_counts else ""
            if all(action.region != item.region for action in scouts):
                scouts.append(ScoutAction(item.region, ScoutReason.MONOCULTURE, family_hint=hint))
        for item in holes:
            if all(action.region != item.region for action in scouts):
                scouts.append(ScoutAction(item.region, ScoutReason.HOLE))
        for item in low_diversity:
            if all(action.region != item.region for action in scouts):
                scouts.append(ScoutAction(item.region, ScoutReason.LOW_FAMILY_DIVERSITY))
        scouts = tuple(scouts[:policy.scout_limit])

        covered = sum(1 for item in summaries if item.fresh_count > 0)
        if stale_pruned:
            decision = CartographyDecision(CartographyDecisionKind.PRUNE_STALE_THEN_SCOUT, False, "stale observations were pruned before scouting")
        elif not self.observations:
            decision = CartographyDecision(CartographyDecisionKind.EMPTY, False, "no keyspace observations yet")
        elif monoculture or introducer_capture:
            decision = CartographyDecision(CartographyDecisionKind.SCOUT_MONOCULTURE, False, "one or more regions are dominated by one observed family or introducer")
        elif covered < policy.min_covered_regions or holes:
            decision = CartographyDecision(CartographyDecisionKind.SCOUT_HOLES, False, "local keyspace view has holes or too few covered regions")
        elif low_diversity:
            decision = CartographyDecision(CartographyDecisionKind.SCOUT_MONOCULTURE, False, "some regions need more family diversity")
        else:
            decision = CartographyDecision(CartographyDecisionKind.ACCEPT_COVERAGE, True, "local keyspace coverage passes lab thresholds")

        digest = sha256(KEYSPACE_CARTOGRAPHY_DOMAIN + b":report:" + bencode({
            b"now": now,
            b"summaries": [item.bvalue() for item in summaries],
            b"scouts": [action.bvalue() for action in scouts],
            b"stale_pruned": stale_pruned,
            b"decision": decision.kind.value,
        }))
        return CartographyReport(tuple(summaries), scouts, stale_pruned, decision, digest)
