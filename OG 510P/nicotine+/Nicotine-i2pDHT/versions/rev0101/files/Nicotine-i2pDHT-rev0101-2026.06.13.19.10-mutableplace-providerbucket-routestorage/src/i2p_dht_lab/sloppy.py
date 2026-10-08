"""Canonical + sloppy replica placement guesses.

Canonical Kademlia says store at the k closest nodes.  On an anonymous and
high-latency substrate, that is necessary but probably not sufficient: hot keys
need overflow breadcrumbs, and power users need a way to contribute spare
storage without pretending to be the mathematically closest nodes.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ids import bucket_index, xor_distance
from .routing import Contact


@dataclass(frozen=True)
class SloppyPolicy:
    canonical_k: int = 20
    sloppy_budget: int = 8
    max_same_bucket_sloppy: int = 2
    prefer_low_rtt: bool = True

    def validate(self) -> None:
        if self.canonical_k <= 0:
            raise ValueError("canonical_k must be positive")
        if self.sloppy_budget < 0:
            raise ValueError("sloppy_budget must not be negative")
        if self.max_same_bucket_sloppy <= 0:
            raise ValueError("max_same_bucket_sloppy must be positive")


@dataclass(frozen=True)
class ReplicaPlacement:
    canonical: tuple[Contact, ...]
    sloppy: tuple[Contact, ...]

    @property
    def all_replicas(self) -> tuple[Contact, ...]:
        return self.canonical + self.sloppy


def _sloppy_score(contact: Contact, target: bytes, *, prefer_low_rtt: bool) -> tuple[int, int, int]:
    rtt = contact.rtt_ms if contact.rtt_ms is not None else 10_000
    # Work bits are a weak positive signal: not trust, just cheap friction paid.
    work_penalty = -contact.work_bits
    distance = xor_distance(contact.node_id, target)
    return (rtt if prefer_low_rtt else 0, work_penalty, distance)


def plan_replica_placement(candidates: list[Contact], target: bytes, *, policy: SloppyPolicy, lookup_path: list[Contact] | None = None) -> ReplicaPlacement:
    """Select canonical closest replicas plus diverse sloppy/breadcrumb replicas."""

    policy.validate()
    ordered = sorted(candidates, key=lambda contact: xor_distance(contact.node_id, target))
    canonical = tuple(ordered[: policy.canonical_k])
    canonical_ids = {contact.node_id for contact in canonical}

    pool: dict[bytes, Contact] = {contact.node_id: contact for contact in candidates if contact.node_id not in canonical_ids}
    # Breadcrumbs seen during lookup get first chance at sloppy storage, because
    # they are exactly the nodes future queries may encounter on the same path.
    if lookup_path:
        for contact in lookup_path:
            if contact.node_id not in canonical_ids:
                pool[contact.node_id] = contact

    sloppy: list[Contact] = []
    bucket_counts: dict[int, int] = {}
    for contact in sorted(pool.values(), key=lambda c: _sloppy_score(c, target, prefer_low_rtt=policy.prefer_low_rtt)):
        idx = bucket_index(target, contact.node_id)
        if bucket_counts.get(idx, 0) >= policy.max_same_bucket_sloppy:
            continue
        sloppy.append(contact)
        bucket_counts[idx] = bucket_counts.get(idx, 0) + 1
        if len(sloppy) >= policy.sloppy_budget:
            break

    return ReplicaPlacement(canonical=canonical, sloppy=tuple(sloppy))
