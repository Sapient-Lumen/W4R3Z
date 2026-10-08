"""Contact-lease quorum pressure for resilient DHT entrances.

``contactlease.py`` made individual entrances fresh and monotonic.  rev0019 adds
the harder portfolio question: are our fresh contacts independent enough to use
as an entrance set, or did one seed/garden/source family hand us a beautiful but
captured-looking portfolio?

This is still local evidence.  The word quorum here does not mean consensus.  It
means a client refuses to let one source path, one introducer family, or one
purpose class silently become the entrance truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .contactlease import ContactLease, ContactLeaseBook, ContactLeasePurpose, ContactLeaseVerdict
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .ids import DOMAIN, sha256, xor_distance

LEASE_QUORUM_DOMAIN = DOMAIN + b":lease-quorum-v1:"


class LeaseSourceKind(str, Enum):
    DIRECT_INVITE = "direct_invite"
    GARDEN_SEED = "garden_seed"
    ROUTE_GOSSIP = "route_gossip"
    MUTABLE_SEED_HEAD = "mutable_seed_head"
    CACHE = "cache"
    CLASSIC_BRIDGE = "classic_bridge"


class LeaseQuorumDecisionKind(str, Enum):
    ACCEPT_LEASE_QUORUM = "accept_lease_quorum"
    CONTINUE_NO_VALID_LEASES = "continue_no_valid_leases"
    CONTINUE_LOW_NODE_DIVERSITY = "continue_low_node_diversity"
    CONTINUE_LOW_SOURCE_DIVERSITY = "continue_low_source_diversity"
    CONTINUE_LOW_PURPOSE_COVERAGE = "continue_low_purpose_coverage"
    QUARANTINE_FORK_PRESSURE = "quarantine_fork_pressure"
    QUARANTINE_SOURCE_CAPTURE = "quarantine_source_capture"


@dataclass(frozen=True)
class LeaseObservation:
    lease: ContactLease
    source_kind: LeaseSourceKind
    source_family: str
    path_family: str
    observed_at: int
    note: str = ""

    def __post_init__(self) -> None:
        if not self.source_family or not self.path_family:
            raise ValueError("lease observation needs source and path family hints")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"lease_hash": self.lease.lease_hash,
            b"lease_family": self.lease.family_id,
            b"source_kind": self.source_kind.value,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"observed_at": self.observed_at,
            b"note": self.note,
        }


@dataclass(frozen=True)
class LeaseQuorumPolicy:
    min_valid_leases: int = 5
    min_node_families: int = 3
    min_source_families: int = 3
    min_path_families: int = 2
    max_per_node_family: int = 2
    max_per_source_family: int = 2
    min_seed_gates: int = 1
    min_route_contacts: int = 2
    required_purposes: frozenset[ContactLeasePurpose] = frozenset({ContactLeasePurpose.ROUTE, ContactLeasePurpose.SEED_GATE})
    min_work_bits: int = 0

    def validate(self) -> None:
        for value in (self.min_valid_leases, self.min_node_families, self.min_source_families, self.min_path_families, self.max_per_node_family, self.max_per_source_family):
            if value <= 0:
                raise ValueError("lease quorum thresholds must be positive")
        if self.min_seed_gates < 0 or self.min_route_contacts < 0 or self.min_work_bits < 0:
            raise ValueError("lease quorum counts/work must be non-negative")


@dataclass(frozen=True)
class LeaseQuorumDecision:
    kind: LeaseQuorumDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class LeaseQuorumReport:
    selected_observations: tuple[LeaseObservation, ...]
    invalid_observations: tuple[LeaseObservation, ...]
    verdicts: tuple[ContactLeaseVerdict, ...]
    node_family_counts: dict[str, int]
    source_family_counts: dict[str, int]
    path_family_counts: dict[str, int]
    purpose_counts: dict[str, int]
    fork_pressure: bool
    decision: LeaseQuorumDecision
    transcript_digest: bytes

    @property
    def needs_more_sources(self) -> bool:
        return not self.decision.accept


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def assess_lease_quorum(
    observations: Iterable[LeaseObservation],
    *,
    now: int,
    target: bytes | None = None,
    policy: LeaseQuorumPolicy | None = None,
    lease_book: ContactLeaseBook | None = None,
) -> LeaseQuorumReport:
    policy = policy or LeaseQuorumPolicy()
    policy.validate()
    book = lease_book or ContactLeaseBook()
    valid: list[LeaseObservation] = []
    invalid: list[LeaseObservation] = []
    verdicts: list[ContactLeaseVerdict] = []
    for observation in observations:
        verdict = book.observe(observation.lease, now=now, min_work_bits=policy.min_work_bits)
        verdicts.append(verdict)
        if verdict.accepted:
            valid.append(observation)
        else:
            invalid.append(observation)
    target = target or (b"\x00" * 32)

    node_capped = select_family_capped(
        valid,
        family_of=lambda obs: obs.lease.family_id,
        sort_key=lambda obs: (xor_distance(obs.lease.node_id, target), -obs.lease.sequence, obs.source_kind.value, obs.lease.node_id),
        limit=max(policy.min_valid_leases, policy.min_node_families * policy.max_per_node_family, policy.min_source_families * policy.max_per_source_family),
        max_per_family=policy.max_per_node_family,
    )
    selected = tuple(select_family_capped(
        node_capped,
        family_of=lambda obs: obs.source_family,
        sort_key=lambda obs: (xor_distance(obs.lease.node_id, target), obs.path_family, obs.lease.node_id),
        limit=max(policy.min_valid_leases, policy.min_source_families * policy.max_per_source_family),
        max_per_family=policy.max_per_source_family,
    ))

    node_diversity = analyze_family_diversity(selected, family_of=lambda obs: obs.lease.family_id, policy=FamilyDiversityPolicy(policy.min_node_families, policy.max_per_node_family))
    source_diversity = analyze_family_diversity(selected, family_of=lambda obs: obs.source_family, policy=FamilyDiversityPolicy(policy.min_source_families, policy.max_per_source_family))
    path_counts = _counts(obs.path_family for obs in selected)
    purpose_counts: dict[str, int] = {}
    for obs in selected:
        for purpose in obs.lease.purposes:
            purpose_counts[purpose.value] = purpose_counts.get(purpose.value, 0) + 1

    if book.fork_pressure:
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.QUARANTINE_FORK_PRESSURE, False, "contact-lease fork pressure observed while building entrance quorum")
    elif not selected:
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.CONTINUE_NO_VALID_LEASES, False, "no fresh valid lease observations")
    elif len(selected) < policy.min_valid_leases or not node_diversity.passes(FamilyDiversityPolicy(policy.min_node_families, policy.max_per_node_family)):
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.CONTINUE_LOW_NODE_DIVERSITY, False, "valid leases lack enough node-family diversity")
    elif not source_diversity.passes(FamilyDiversityPolicy(policy.min_source_families, policy.max_per_source_family)):
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.CONTINUE_LOW_SOURCE_DIVERSITY, False, "valid leases arrived through too few source families")
    elif len([family for family, count in path_counts.items() if count > 0]) < policy.min_path_families:
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.QUARANTINE_SOURCE_CAPTURE, False, "lease portfolio has source diversity but low path-family diversity")
    elif any(purpose_counts.get(purpose.value, 0) <= 0 for purpose in policy.required_purposes) or purpose_counts.get(ContactLeasePurpose.SEED_GATE.value, 0) < policy.min_seed_gates or purpose_counts.get(ContactLeasePurpose.ROUTE.value, 0) < policy.min_route_contacts:
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.CONTINUE_LOW_PURPOSE_COVERAGE, False, "leases are diverse but do not cover required entrance purposes")
    else:
        decision = LeaseQuorumDecision(LeaseQuorumDecisionKind.ACCEPT_LEASE_QUORUM, True, "fresh leases have enough node/source/path diversity and purpose coverage")

    digest = sha256(LEASE_QUORUM_DOMAIN + b":report:" + bencode({
        b"now": now,
        b"selected": [obs.bvalue() for obs in selected],
        b"invalid": [obs.bvalue() for obs in invalid],
        b"node_families": {family: count for family, count in sorted(node_diversity.family_counts.items())},
        b"source_families": {family: count for family, count in sorted(source_diversity.family_counts.items())},
        b"path_families": {family: count for family, count in sorted(path_counts.items())},
        b"purpose_counts": {purpose: count for purpose, count in sorted(purpose_counts.items())},
        b"decision": decision.kind.value,
    }))
    return LeaseQuorumReport(selected, tuple(invalid), tuple(verdicts), node_diversity.family_counts, source_diversity.family_counts, path_counts, purpose_counts, book.fork_pressure, decision, digest)
