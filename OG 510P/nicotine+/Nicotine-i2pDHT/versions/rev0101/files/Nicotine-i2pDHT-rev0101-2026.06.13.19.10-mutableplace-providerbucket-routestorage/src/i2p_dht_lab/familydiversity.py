"""Shared local family-diversity helpers.

The cube accumulated several near-identical family caps while pressure-testing
provider probes, mutable-head observations, garden refusals, and latency fronts.
rev0014 keeps the historical modules intact but factors the common *shape* into
one tiny helper: count families, cap per family, and detect monoculture/capture
pressure.

This is intentionally not an independence oracle.  A ``family`` label is a local
hint: router family, garden operator family, invite channel, path class, trust
bucket, or any other caller-defined partition.  The helper only prevents the
caller from accidentally treating many same-family events as diverse evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FamilyDiversityPolicy:
    min_families: int = 2
    max_per_family: int = 1
    max_dominant_fraction: float = 0.67
    # Compatibility surface for rev0024 branchlets that reason in ppm.
    max_fraction_ppm: int | None = None

    def validate(self) -> None:
        if self.min_families <= 0:
            raise ValueError("min_families must be positive")
        if self.max_per_family <= 0:
            raise ValueError("max_per_family must be positive")
        if self.max_fraction_ppm is not None:
            if not (1 <= self.max_fraction_ppm <= 1_000_000):
                raise ValueError("max_fraction_ppm must be in [1, 1000000]")
        if not (0 < self.max_dominant_fraction <= 1):
            raise ValueError("max_dominant_fraction must be in (0, 1]")

    @property
    def dominant_fraction_limit(self) -> float:
        return self.max_dominant_fraction if self.max_fraction_ppm is None else self.max_fraction_ppm / 1_000_000


@dataclass(frozen=True)
class FamilyDiversityReport:
    total_items: int
    counted_items: int
    family_counts: dict[str, int]
    dominant_family: str
    dominant_fraction: float
    uncapped_family_counts: dict[str, int]
    required_min_families: int = 2
    required_dominant_fraction: float = 0.67

    @property
    def families(self) -> frozenset[str]:
        return frozenset(self.family_counts)

    @property
    def uncapped_families(self) -> frozenset[str]:
        return frozenset(self.uncapped_family_counts)

    @property
    def is_monoculture(self) -> bool:
        return self.counted_items > 0 and len(self.family_counts) <= 1

    def passes(self, policy: FamilyDiversityPolicy) -> bool:
        policy.validate()
        if self.counted_items == 0:
            return False
        return len(self.family_counts) >= policy.min_families and self.dominant_fraction <= policy.dominant_fraction_limit

    @property
    def accept(self) -> bool:
        return self.counted_items > 0 and len(self.family_counts) >= self.required_min_families and self.dominant_fraction <= self.required_dominant_fraction


def family_counts(items: Iterable[T], family_of: Callable[[T], str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        family = family_of(item)
        counts[family] = counts.get(family, 0) + 1
    return counts


def select_family_capped(
    items: Iterable[T],
    *,
    family_of: Callable[[T], str],
    sort_key: Callable[[T], object] | None = None,
    limit: int | None = None,
    max_per_family: int = 1,
) -> tuple[T, ...]:
    """Select items while enforcing a same-family cap.

    ``sort_key`` is caller-owned so this helper does not know about XOR distance,
    latency, trust score, or head sequence.  The important property is that family
    capping happens after sorting but before acceptance.
    """
    if max_per_family <= 0:
        raise ValueError("max_per_family must be positive")
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")
    ordered = list(items)
    if sort_key is not None:
        ordered.sort(key=sort_key)
    selected: list[T] = []
    counts: dict[str, int] = {}
    for item in ordered:
        family = family_of(item)
        if counts.get(family, 0) >= max_per_family:
            continue
        selected.append(item)
        counts[family] = counts.get(family, 0) + 1
        if limit is not None and len(selected) >= limit:
            break
    return tuple(selected)


def analyze_family_diversity(
    items: Iterable[T],
    policy_or_family_of: FamilyDiversityPolicy | Callable[[T], str] | None = None,
    *,
    family_of: Callable[[T], str] | None = None,
    policy: FamilyDiversityPolicy | None = None,
    sort_key: Callable[[T], object] | None = None,
    limit: int | None = None,
) -> FamilyDiversityReport:
    """Analyze family spread while supporting historical call shapes.

    Current code usually calls ``analyze_family_diversity(items, family_of=...)``.
    Some rev0024 branchlets intentionally pass a tuple of family strings plus a
    positional ``FamilyDiversityPolicy``.  Supporting both keeps the refactor
    boring and lets the audit surface find real drift instead of API trivia.
    """
    if isinstance(policy_or_family_of, FamilyDiversityPolicy):
        policy = policy_or_family_of
    elif policy_or_family_of is not None:
        family_of = policy_or_family_of  # type: ignore[assignment]
    policy = policy or FamilyDiversityPolicy()
    policy.validate()
    if family_of is None:
        family_of = lambda item: str(item)  # type: ignore[assignment]
    item_tuple = tuple(items)
    uncapped_counts = family_counts(item_tuple, family_of)
    counted = select_family_capped(
        item_tuple,
        family_of=family_of,
        sort_key=sort_key,
        limit=limit,
        max_per_family=policy.max_per_family,
    )
    capped_counts = family_counts(counted, family_of)
    if capped_counts:
        dominant_family, dominant_count = sorted(capped_counts.items(), key=lambda item: (-item[1], item[0]))[0]
        dominant_fraction = dominant_count / len(counted)
    else:
        dominant_family = ""
        dominant_fraction = 0.0
    report = FamilyDiversityReport(
        total_items=len(item_tuple),
        counted_items=len(counted),
        family_counts=capped_counts,
        dominant_family=dominant_family,
        dominant_fraction=dominant_fraction,
        uncapped_family_counts=uncapped_counts,
        required_min_families=policy.min_families,
        required_dominant_fraction=policy.dominant_fraction_limit,
    )
    # Attach a policy-sensitive accept property for branchlets by using a tiny
    # dynamic subclass only when needed would be overkill; instead, store the
    # adjusted threshold by mutating frozen object internals is forbidden.
    # Callers that need policy-specific truth should use ``report.passes(policy)``.
    return report
