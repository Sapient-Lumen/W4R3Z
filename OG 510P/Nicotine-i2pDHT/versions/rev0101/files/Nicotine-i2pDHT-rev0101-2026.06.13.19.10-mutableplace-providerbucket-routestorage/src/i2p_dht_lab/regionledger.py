"""Garden region-ledger scheduling for provider/mutable reannounce work.

A region sweep is cheap only if the garden remembers what it is sweeping.  This
module adds a tiny ledger in front of ``sweep.py``: advertisements enter with
source-family hints, tombstones can suppress resurrection, and batch planning is
region-aware instead of FIFO.

The ledger is local operational memory.  It does not decide global truth about a
record; it decides whether this garden should spend bandwidth reannouncing it in
this interval.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .ids import DOMAIN, sha256
from .sweep import AdvertKind, Advertisement, SweepPolicy, key_region

REGION_LEDGER_DOMAIN = DOMAIN + b":region-ledger-v1:"


class RegionLedgerDecisionKind(str, Enum):
    PLAN_READY = "plan_ready"
    CONTINUE_NO_DUE_WORK = "continue_no_due_work"
    QUARANTINE_SOURCE_MONOCULTURE = "quarantine_source_monoculture"
    TOMBSTONE_ONLY = "tombstone_only"


@dataclass(frozen=True)
class RegionLedgerPolicy:
    sweep_policy: SweepPolicy = SweepPolicy(region_prefix_bits=8, max_batch_weight=160)
    max_batches: int = 8
    max_per_source_family: int = 32
    min_source_families_for_large_batch: int = 2
    large_batch_threshold: int = 64
    tombstone_priority: bool = True

    def validate(self) -> None:
        self.sweep_policy.validate()
        if self.max_batches <= 0 or self.max_per_source_family <= 0:
            raise ValueError("ledger batch limits must be positive")
        if self.min_source_families_for_large_batch <= 0 or self.large_batch_threshold <= 0:
            raise ValueError("ledger diversity thresholds must be positive")


@dataclass(frozen=True)
class LedgerAdvertisement:
    advertisement: Advertisement
    source_family: str
    first_seen_at: int
    last_seen_at: int
    last_published_at: int = 0

    @property
    def key(self) -> bytes:
        return self.advertisement.key

    @property
    def kind(self) -> AdvertKind:
        return self.advertisement.kind

    @property
    def namespace(self) -> str:
        return self.advertisement.namespace

    @property
    def weight(self) -> int:
        return self.advertisement.weight

    def identity_tuple(self) -> tuple[str, str, bytes]:
        return (self.namespace, self.kind.value, self.key)

    def due(self, *, now: int, policy: RegionLedgerPolicy) -> bool:
        return now - self.last_published_at >= policy.sweep_policy.interval_seconds

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"key": self.key,
            b"kind": self.kind.value,
            b"namespace": self.namespace,
            b"source_family": self.source_family,
            b"first_seen_at": self.first_seen_at,
            b"last_seen_at": self.last_seen_at,
            b"last_published_at": self.last_published_at,
            b"weight": self.weight,
        }


@dataclass(frozen=True)
class RegionTombstone:
    key: bytes
    kind: AdvertKind
    namespace: str
    issuer_family: str
    issued_at: int
    expires_at: int
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.key or not self.namespace or not self.issuer_family:
            raise ValueError("tombstone key, namespace, and issuer_family are required")
        if self.expires_at <= self.issued_at:
            raise ValueError("tombstone expires_at must be after issued_at")

    @property
    def digest(self) -> bytes:
        return sha256(REGION_LEDGER_DOMAIN + b":tombstone:" + bencode(self.bvalue()))

    def identity_tuple(self) -> tuple[str, str, bytes]:
        return (self.namespace, self.kind.value, self.key)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def region(self, *, policy: RegionLedgerPolicy) -> int:
        return key_region(self.key, prefix_bits=policy.sweep_policy.region_prefix_bits)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"key": self.key,
            b"kind": self.kind.value,
            b"namespace": self.namespace,
            b"issuer_family": self.issuer_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"reason": self.reason[:160],
        }


@dataclass(frozen=True)
class RegionLedgerBatch:
    region: int
    due_at: int
    advertisements: tuple[LedgerAdvertisement, ...]
    tombstones: tuple[RegionTombstone, ...]

    @property
    def total_weight(self) -> int:
        return sum(item.weight for item in self.advertisements) + len(self.tombstones)

    @property
    def source_families(self) -> frozenset[str]:
        # Normal ledger batches contain LedgerAdvertisement objects, but some
        # audit fixtures construct RegionLedgerBatch directly from bare
        # Advertisement values. Treat missing source_family as an unknown local
        # audit hint rather than crashing the audit surface.
        families = [getattr(item, "source_family", "unknown") for item in self.advertisements]
        families.extend(item.issuer_family for item in self.tombstones)
        return frozenset(families)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"region": self.region,
            b"due_at": self.due_at,
            b"advertisements": [item.bvalue() for item in self.advertisements],
            b"tombstones": [item.bvalue() for item in self.tombstones],
            b"total_weight": self.total_weight,
        }


@dataclass(frozen=True)
class RegionLedgerDecision:
    kind: RegionLedgerDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class RegionLedgerReport:
    batches: tuple[RegionLedgerBatch, ...]
    suppressed_advertisements: tuple[LedgerAdvertisement, ...]
    source_family_counts: dict[str, int]
    decision: RegionLedgerDecision
    transcript_digest: bytes

    @property
    def batch_count(self) -> int:
        return len(self.batches)

    @property
    def total_weight(self) -> int:
        return sum(batch.total_weight for batch in self.batches)


@dataclass
class RegionLedger:
    advertisements: dict[tuple[str, str, bytes], LedgerAdvertisement] = field(default_factory=dict)
    tombstones: dict[tuple[str, str, bytes], RegionTombstone] = field(default_factory=dict)

    def ingest(self, advertisements: Iterable[Advertisement], *, source_family: str, now: int) -> int:
        if not source_family:
            raise ValueError("source_family is required")
        count = 0
        for advert in advertisements:
            advert.validate()
            key = (advert.namespace, advert.kind.value, advert.key)
            existing = self.advertisements.get(key)
            if existing is None:
                self.advertisements[key] = LedgerAdvertisement(advert, source_family, now, now, advert.last_published_at)
            else:
                self.advertisements[key] = replace(existing, advertisement=advert, source_family=source_family, last_seen_at=now, last_published_at=max(existing.last_published_at, advert.last_published_at))
            count += 1
        return count

    def add_tombstone(self, tombstone: RegionTombstone) -> None:
        existing = self.tombstones.get(tombstone.identity_tuple())
        if existing is None or tombstone.issued_at >= existing.issued_at:
            self.tombstones[tombstone.identity_tuple()] = tombstone

    def live_tombstones(self, *, now: int) -> tuple[RegionTombstone, ...]:
        return tuple(tombstone for tombstone in self.tombstones.values() if tombstone.live(now=now))

    def suppressed(self, *, now: int) -> tuple[LedgerAdvertisement, ...]:
        live_keys = {tombstone.identity_tuple() for tombstone in self.live_tombstones(now=now)}
        return tuple(advert for key, advert in sorted(self.advertisements.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])) if key in live_keys)

    def mark_published(self, batch: RegionLedgerBatch, *, published_at: int) -> None:
        for item in batch.advertisements:
            key = item.identity_tuple()
            current = self.advertisements.get(key)
            if current is not None:
                self.advertisements[key] = replace(current, last_published_at=published_at)

    def plan(self, *, now: int, policy: RegionLedgerPolicy | None = None) -> RegionLedgerReport:
        policy = policy or RegionLedgerPolicy()
        policy.validate()
        suppressed = self.suppressed(now=now)
        suppressed_keys = {item.identity_tuple() for item in suppressed}
        due_adverts = [advert for advert in self.advertisements.values() if advert.identity_tuple() not in suppressed_keys and advert.due(now=now, policy=policy)]
        live_tombstones = list(self.live_tombstones(now=now))

        candidate_family_counts: dict[str, int] = {}
        for item in due_adverts:
            candidate_family_counts[item.source_family] = candidate_family_counts.get(item.source_family, 0) + 1
        for item in live_tombstones:
            candidate_family_counts[item.issuer_family] = candidate_family_counts.get(item.issuer_family, 0) + 1

        candidate_count = len(due_adverts) + len(live_tombstones)
        if candidate_count == 0:
            digest = sha256(REGION_LEDGER_DOMAIN + b":report:" + bencode({b"now": now, b"batches": [], b"suppressed": [item.bvalue() for item in suppressed]}))
            return RegionLedgerReport((), suppressed, {}, RegionLedgerDecision(RegionLedgerDecisionKind.CONTINUE_NO_DUE_WORK, False, "no due region work"), digest)

        diversity = analyze_family_diversity(
            list(due_adverts) + list(live_tombstones),
            family_of=lambda item: item.source_family if isinstance(item, LedgerAdvertisement) else item.issuer_family,
            policy=FamilyDiversityPolicy(min_families=policy.min_source_families_for_large_batch, max_per_family=max(policy.max_per_source_family, 1)),
        )
        if candidate_count >= policy.large_batch_threshold and len(diversity.uncapped_families) < policy.min_source_families_for_large_batch:
            digest = sha256(REGION_LEDGER_DOMAIN + b":report-quarantine:" + bencode({b"now": now, b"families": {family: count for family, count in sorted(candidate_family_counts.items())}}))
            return RegionLedgerReport((), suppressed, candidate_family_counts, RegionLedgerDecision(RegionLedgerDecisionKind.QUARANTINE_SOURCE_MONOCULTURE, False, "large due region batch is sourced from too few families"), digest)

        by_region_adverts: dict[int, list[LedgerAdvertisement]] = {}
        for advert in select_family_capped(
            due_adverts,
            family_of=lambda item: item.source_family,
            sort_key=lambda item: (key_region(item.key, prefix_bits=policy.sweep_policy.region_prefix_bits), item.kind.value, item.namespace, item.key),
            limit=None,
            max_per_family=policy.max_per_source_family,
        ):
            region = key_region(advert.key, prefix_bits=policy.sweep_policy.region_prefix_bits)
            by_region_adverts.setdefault(region, []).append(advert)

        by_region_tombstones: dict[int, list[RegionTombstone]] = {}
        for tombstone in live_tombstones:
            by_region_tombstones.setdefault(tombstone.region(policy=policy), []).append(tombstone)

        all_regions = sorted(set(by_region_adverts) | set(by_region_tombstones))
        if policy.tombstone_priority:
            all_regions.sort(key=lambda region: (0 if by_region_tombstones.get(region) else 1, region))

        batches: list[RegionLedgerBatch] = []
        for region in all_regions:
            adverts = sorted(by_region_adverts.get(region, []), key=lambda item: (item.kind.value, item.namespace, item.key))
            tombstones = tuple(sorted(by_region_tombstones.get(region, []), key=lambda item: (item.issued_at, item.digest), reverse=True))
            current: list[LedgerAdvertisement] = []
            current_tombstones = tombstones
            current_weight = len(current_tombstones)
            for advert in adverts:
                if current and current_weight + advert.weight > policy.sweep_policy.max_batch_weight:
                    batches.append(RegionLedgerBatch(region, now, tuple(current), current_tombstones))
                    current = []
                    current_tombstones = ()
                    current_weight = 0
                current.append(advert)
                current_weight += advert.weight
            if current or current_tombstones:
                batches.append(RegionLedgerBatch(region, now, tuple(current), current_tombstones))
            if len(batches) >= policy.max_batches:
                batches = batches[:policy.max_batches]
                break

        if batches and not due_adverts and live_tombstones:
            decision = RegionLedgerDecision(RegionLedgerDecisionKind.TOMBSTONE_ONLY, True, "only tombstone reannounce work is due")
        elif batches:
            decision = RegionLedgerDecision(RegionLedgerDecisionKind.PLAN_READY, True, "region-ledger sweep plan ready")
        else:
            decision = RegionLedgerDecision(RegionLedgerDecisionKind.CONTINUE_NO_DUE_WORK, False, "family caps suppressed all due work")

        digest = sha256(REGION_LEDGER_DOMAIN + b":report:" + bencode({
            b"now": now,
            b"batches": [batch.bvalue() for batch in batches],
            b"suppressed": [item.bvalue() for item in suppressed],
            b"families": {family: count for family, count in sorted(candidate_family_counts.items())},
            b"decision": decision.kind.value,
        }))
        return RegionLedgerReport(tuple(batches), suppressed, candidate_family_counts, decision, digest)
