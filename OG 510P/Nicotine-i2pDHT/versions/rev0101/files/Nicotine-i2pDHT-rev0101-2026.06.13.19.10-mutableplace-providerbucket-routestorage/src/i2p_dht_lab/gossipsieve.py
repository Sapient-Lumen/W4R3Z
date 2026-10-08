"""Gossip sieve for entrance growth without introducer capture.

Signed route/contact hints are useful only if they do not silently spend a
node's interest budget or collapse into one introducer family. This module joins
contact leases, route attestations, introducer families, path families, and
metadata-interest points before later layers spend real work.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .contactlease import ContactLeasePurpose
from .ids import DOMAIN, sha256, xor_distance
from .routeattest import RouteAttestation
from .contactlease import ContactLease

GOSSIP_SIEVE_DOMAIN = DOMAIN + b":gossip-sieve-v2:"


class GossipSieveDecisionKind(str, Enum):
    ACCEPT_GOSSIP_BATCH = "accept_gossip_batch"
    REJECT_INTEREST_BUDGET = "reject_interest_budget"
    REJECT_BAD_LEASE_OR_ATTESTATION = "reject_bad_lease_or_attestation"
    HOLD_LOW_CONTACT_DIVERSITY = "hold_low_contact_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_INTRODUCER_CAPTURE = "quarantine_introducer_capture"
    EMPTY = "empty"


@dataclass(frozen=True)
class GossipCandidate:
    lease: ContactLease
    introducer_node_id: bytes
    introducer_family: str
    attestation: RouteAttestation
    distance_rank: int
    interest_points: int = 1

    def __post_init__(self) -> None:
        if len(self.introducer_node_id) != 32:
            raise ValueError("introducer node id must be 32 bytes")
        if not self.introducer_family:
            raise ValueError("introducer family is required")
        if self.distance_rank < 0 or self.interest_points < 0:
            raise ValueError("distance and interest counters must be non-negative")

    @property
    def contact_family(self) -> str:
        return self.lease.family_id

    @property
    def path_family(self) -> str:
        return self.attestation.path_family

    @property
    def candidate_digest(self) -> bytes:
        return sha256(GOSSIP_SIEVE_DOMAIN + b":candidate:" + self.lease.lease_hash + self.attestation.attestation_digest + self.introducer_node_id)


@dataclass(frozen=True)
class GossipSievePolicy:
    min_contact_families: int = 3
    min_path_families: int = 2
    min_introducer_families: int = 2
    max_per_introducer_family: int = 2
    max_interest_points: int = 20
    max_selected: int = 8

    def validate(self) -> None:
        for value in (self.min_contact_families, self.min_path_families, self.min_introducer_families, self.max_per_introducer_family, self.max_interest_points, self.max_selected):
            if value <= 0:
                raise ValueError("gossip sieve policy thresholds must be positive")


@dataclass(frozen=True)
class GossipSieveReport:
    candidates: tuple[GossipCandidate, ...]
    selected: tuple[GossipCandidate, ...]
    contact_family_counts: dict[str, int]
    introducer_family_counts: dict[str, int]
    path_family_counts: dict[str, int]
    decision_kind: GossipSieveDecisionKind
    accept: bool
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _inc(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1


def _valid(candidate: GossipCandidate, *, now: int) -> bool:
    if not candidate.lease.verify(now=now):
        return False
    if candidate.attestation.lease_hash != candidate.lease.lease_hash:
        return False
    if candidate.attestation.purpose is not ContactLeasePurpose.ROUTE:
        return False
    if not candidate.attestation.live(now=now) or not candidate.attestation.signature_valid():
        return False
    return True


def sieve_gossip_candidates(candidates: Iterable[GossipCandidate], *, now: int, target: bytes, policy: GossipSievePolicy | None = None) -> GossipSieveReport:
    if len(target) != 32:
        raise ValueError("gossip target must be 32 bytes")
    policy = policy or GossipSievePolicy()
    policy.validate()
    candidate_tuple = tuple(candidates)
    if not candidate_tuple:
        digest = sha256(GOSSIP_SIEVE_DOMAIN + b":empty:" + target)
        return GossipSieveReport((), (), {}, {}, {}, GossipSieveDecisionKind.EMPTY, False, digest)
    if any(item.interest_points > policy.max_interest_points for item in candidate_tuple):
        digest = sha256(GOSSIP_SIEVE_DOMAIN + b":interest-stop:" + b"".join(item.candidate_digest for item in candidate_tuple))
        return GossipSieveReport(candidate_tuple, (), {}, {}, {}, GossipSieveDecisionKind.REJECT_INTEREST_BUDGET, False, digest)

    selected: list[GossipCandidate] = []
    intro_counts: dict[str, int] = {}
    for item in sorted(candidate_tuple, key=lambda c: (c.distance_rank, xor_distance(c.lease.node_id, target), c.candidate_digest)):
        if not _valid(item, now=now):
            continue
        if intro_counts.get(item.introducer_family, 0) >= policy.max_per_introducer_family:
            continue
        selected.append(item)
        _inc(intro_counts, item.introducer_family)
        if len(selected) >= policy.max_selected:
            break

    contact_counts: dict[str, int] = {}
    path_counts: dict[str, int] = {}
    intro_counts = {}
    for item in selected:
        _inc(contact_counts, item.contact_family)
        _inc(path_counts, item.path_family)
        _inc(intro_counts, item.introducer_family)

    if not selected:
        decision = GossipSieveDecisionKind.REJECT_BAD_LEASE_OR_ATTESTATION
        accept = False
    elif len(intro_counts) < policy.min_introducer_families and len(selected) >= max(2, policy.min_contact_families):
        decision = GossipSieveDecisionKind.QUARANTINE_INTRODUCER_CAPTURE
        accept = False
    elif len(contact_counts) < policy.min_contact_families:
        decision = GossipSieveDecisionKind.HOLD_LOW_CONTACT_DIVERSITY
        accept = False
    elif len(path_counts) < policy.min_path_families:
        decision = GossipSieveDecisionKind.HOLD_LOW_PATH_DIVERSITY
        accept = False
    else:
        decision = GossipSieveDecisionKind.ACCEPT_GOSSIP_BATCH
        accept = True
    digest = sha256(GOSSIP_SIEVE_DOMAIN + b":report:" + bencode({
        b"candidates": [item.candidate_digest for item in candidate_tuple],
        b"selected": [item.candidate_digest for item in selected],
        b"contact": {family: count for family, count in sorted(contact_counts.items())},
        b"intro": {family: count for family, count in sorted(intro_counts.items())},
        b"path": {family: count for family, count in sorted(path_counts.items())},
        b"decision": decision.value,
    }))
    return GossipSieveReport(candidate_tuple, tuple(selected), contact_counts, intro_counts, path_counts, decision, accept, digest)
