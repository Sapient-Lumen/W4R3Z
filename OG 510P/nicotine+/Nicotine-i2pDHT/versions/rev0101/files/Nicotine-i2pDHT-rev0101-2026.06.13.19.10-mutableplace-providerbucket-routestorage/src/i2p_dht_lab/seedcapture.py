"""Seed-portfolio capture pressure.

A mutable seed portfolio is a gift and a trap. It can help a DHT survive without
central entrances, but a captured portfolio can bias a new node into a narrow
neighborhood. rev0010 makes that risk executable with diversity/capture scoring
and a tiny round-robin selector that avoids taking all entrances from the same
channel or family first.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .mutable_future import SeedPortfolio, SeedPortfolioEntry


class SeedCaptureKind(str, Enum):
    HEALTHY = "healthy"
    ATTACKER_WEIGHT_TOO_HIGH = "attacker_weight_too_high"
    CHANNEL_MONOCULTURE = "channel_monoculture"
    FAMILY_MONOCULTURE = "family_monoculture"
    TOO_FEW_GARDENS = "too_few_gardens"
    EMPTY = "empty"


@dataclass(frozen=True)
class SeedCapturePolicy:
    max_attacker_weight_fraction: float = 0.25
    max_single_channel_fraction: float = 0.45
    max_single_family_fraction: float = 0.45
    min_channels: int = 3
    min_families: int = 3
    min_gardens: int = 2


@dataclass(frozen=True)
class SeedCapturePressure:
    kind: SeedCaptureKind
    total_entries: int
    total_weight: int
    attacker_weight_fraction: float
    max_channel_fraction: float
    max_family_fraction: float
    channel_count: int
    family_count: int
    garden_count: int
    reason: str

    @property
    def healthy(self) -> bool:
        return self.kind is SeedCaptureKind.HEALTHY


def _fraction(max_weight: int, total: int) -> float:
    return 0.0 if total <= 0 else max_weight / total


def analyze_seed_capture_pressure(
    portfolio: SeedPortfolio,
    *,
    node_families: Mapping[bytes, str] | None = None,
    attacker_node_ids: Iterable[bytes] = (),
    policy: SeedCapturePolicy | None = None,
) -> SeedCapturePressure:
    policy = policy or SeedCapturePolicy()
    entries = tuple(portfolio.entries)
    if not entries:
        return SeedCapturePressure(SeedCaptureKind.EMPTY, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, "portfolio has no entries")
    families = node_families or {}
    attackers = set(attacker_node_ids)
    total_weight = sum(max(0, entry.weight) for entry in entries)
    attacker_weight = sum(max(0, entry.weight) for entry in entries if entry.node_id in attackers)
    by_channel: dict[str, int] = {}
    by_family: dict[str, int] = {}
    for entry in entries:
        weight = max(0, entry.weight)
        by_channel[entry.channel] = by_channel.get(entry.channel, 0) + weight
        family = families.get(entry.node_id, "node:" + entry.node_id.hex()[:16])
        by_family[family] = by_family.get(family, 0) + weight
    attacker_fraction = _fraction(attacker_weight, total_weight)
    max_channel_fraction = _fraction(max(by_channel.values(), default=0), total_weight)
    max_family_fraction = _fraction(max(by_family.values(), default=0), total_weight)
    garden_count = sum(1 for entry in entries if entry.is_gardenish)

    if attacker_fraction > policy.max_attacker_weight_fraction:
        kind = SeedCaptureKind.ATTACKER_WEIGHT_TOO_HIGH
        reason = "known attacker weight exceeds portfolio threshold"
    elif len(by_channel) < policy.min_channels or max_channel_fraction > policy.max_single_channel_fraction:
        kind = SeedCaptureKind.CHANNEL_MONOCULTURE
        reason = "entrance channels are too concentrated"
    elif len(by_family) < policy.min_families or max_family_fraction > policy.max_single_family_fraction:
        kind = SeedCaptureKind.FAMILY_MONOCULTURE
        reason = "routing/contact families are too concentrated"
    elif garden_count < policy.min_gardens:
        kind = SeedCaptureKind.TOO_FEW_GARDENS
        reason = "too few garden/seed-gate entries"
    else:
        kind = SeedCaptureKind.HEALTHY
        reason = "seed portfolio is diverse enough for lab thresholds"
    return SeedCapturePressure(
        kind,
        len(entries),
        total_weight,
        attacker_fraction,
        max_channel_fraction,
        max_family_fraction,
        len(by_channel),
        len(by_family),
        garden_count,
        reason,
    )


def select_diverse_seed_entries(
    portfolio: SeedPortfolio,
    *,
    node_families: Mapping[bytes, str] | None = None,
    limit: int = 16,
) -> tuple[SeedPortfolioEntry, ...]:
    """Pick a bootstrap subset by alternating channel/family pressure."""
    families = node_families or {}
    remaining = list(portfolio.entries)
    selected: list[SeedPortfolioEntry] = []
    channel_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}

    def sort_key(entry: SeedPortfolioEntry) -> tuple[int, int, int, str, bytes]:
        family = families.get(entry.node_id, "node:" + entry.node_id.hex()[:16])
        # Prefer underrepresented channels/families, gardenish entries, then high
        # weight. This is a selector, not a trust proof.
        return (
            channel_counts.get(entry.channel, 0),
            family_counts.get(family, 0),
            0 if entry.is_gardenish else 1,
            -entry.weight,
            entry.node_id,
        )

    while remaining and len(selected) < limit:
        remaining.sort(key=sort_key)
        entry = remaining.pop(0)
        selected.append(entry)
        family = families.get(entry.node_id, "node:" + entry.node_id.hex()[:16])
        channel_counts[entry.channel] = channel_counts.get(entry.channel, 0) + 1
        family_counts[family] = family_counts.get(family, 0) + 1
    return tuple(selected)
