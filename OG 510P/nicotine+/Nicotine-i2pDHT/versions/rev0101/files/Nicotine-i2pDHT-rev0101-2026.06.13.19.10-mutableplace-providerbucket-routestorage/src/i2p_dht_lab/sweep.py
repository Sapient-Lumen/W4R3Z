"""Provider/mutable reannounce sweep scheduling.

Power users will eventually host large key inventories.  A naive loop that
performs a full lookup per key is doomed on a high-latency anonymous substrate.
This module models a better guess: group keys by keyspace region, discover the
region's closest nodes once, and publish many records to that region in a smooth
sweep instead of an enormous burst.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AdvertKind(str, Enum):
    PROVIDER = "provider"
    MUTABLE_HEAD = "mutable_head"
    CONTACT = "contact"


@dataclass(frozen=True)
class Advertisement:
    key: bytes
    kind: AdvertKind
    namespace: str
    weight: int = 1
    last_published_at: int = 0

    def validate(self) -> None:
        if not self.key:
            raise ValueError("advertisement key must not be empty")
        if self.weight <= 0:
            raise ValueError("weight must be positive")
        if not self.namespace:
            raise ValueError("namespace must not be empty")


@dataclass(frozen=True)
class SweepPolicy:
    interval_seconds: int = 22 * 60 * 60
    expiration_seconds: int = 48 * 60 * 60
    region_prefix_bits: int = 8
    max_batch_weight: int = 128

    def validate(self) -> None:
        if self.interval_seconds <= 0:
            raise ValueError("interval must be positive")
        if self.expiration_seconds <= self.interval_seconds:
            raise ValueError("expiration should exceed interval")
        if not (1 <= self.region_prefix_bits <= 32):
            raise ValueError("region prefix bits must be between 1 and 32")
        if self.max_batch_weight <= 0:
            raise ValueError("max batch weight must be positive")


@dataclass(frozen=True)
class SweepBatch:
    due_at: int
    region: int
    advertisements: tuple[Advertisement, ...]

    @property
    def total_weight(self) -> int:
        return sum(item.weight for item in self.advertisements)


def key_region(key: bytes, *, prefix_bits: int) -> int:
    if not key:
        raise ValueError("key must not be empty")
    if not (1 <= prefix_bits <= len(key) * 8):
        raise ValueError("prefix_bits out of range")
    value = int.from_bytes(key, "big")
    return value >> (len(key) * 8 - prefix_bits)


def _region_due_at(region: int, *, now: int, policy: SweepPolicy) -> int:
    region_count = 1 << policy.region_prefix_bits
    slot = (policy.interval_seconds * region) // region_count
    return now + slot


def plan_reprovide_sweep(advertisements: list[Advertisement], *, now: int, policy: SweepPolicy) -> list[SweepBatch]:
    """Plan smooth, region-grouped re-provides across one interval."""

    policy.validate()
    groups: dict[int, list[Advertisement]] = {}
    for advert in advertisements:
        advert.validate()
        region = key_region(advert.key, prefix_bits=policy.region_prefix_bits)
        groups.setdefault(region, []).append(advert)

    batches: list[SweepBatch] = []
    for region, items in sorted(groups.items()):
        current: list[Advertisement] = []
        current_weight = 0
        for advert in sorted(items, key=lambda item: (item.kind.value, item.namespace, item.key)):
            if current and current_weight + advert.weight > policy.max_batch_weight:
                batches.append(SweepBatch(due_at=_region_due_at(region, now=now, policy=policy), region=region, advertisements=tuple(current)))
                current = []
                current_weight = 0
            current.append(advert)
            current_weight += advert.weight
        if current:
            batches.append(SweepBatch(due_at=_region_due_at(region, now=now, policy=policy), region=region, advertisements=tuple(current)))
    return sorted(batches, key=lambda batch: (batch.due_at, batch.region, len(batch.advertisements)))


def stale_advertisements(advertisements: list[Advertisement], *, now: int, policy: SweepPolicy) -> list[Advertisement]:
    policy.validate()
    return [item for item in advertisements if now - item.last_published_at >= policy.interval_seconds]
