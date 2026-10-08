"""Lease-bound route gossip pressure.

rev0018 made contact leases and route gossip independently testable. rev0019
joins them because the failure mode lives in the seam: a route-gossip batch can
look close, fresh, and family-diverse while carrying contacts whose signed
leases expired, forked, or never authorized route participation.

This module deliberately stays local and deterministic. It does not make a
contact lease into global identity truth. It says: before route gossip repairs
our local table, the selected contacts should be backed by fresh, monotonic,
purpose-scoped lease evidence, and the gossip selection should not be dominated
by one introducer/family.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .contactlease import ContactLease, ContactLeaseBook, ContactLeasePurpose
from .ids import DOMAIN, sha256
from .routegossip import RouteGossipBatch, RouteGossipBook, RouteGossipDecisionKind, RouteGossipPolicy, RouteGossipReport, RouteContact

LEASE_ROUTE_DOMAIN = DOMAIN + b":lease-route-v1:"


class LeaseRouteDecisionKind(str, Enum):
    ACCEPT_LEASED_REPAIR = "accept_leased_repair"
    ACCEPT_EVICT_STALE_THEN_REPAIR = "accept_evict_stale_then_repair"
    CONTINUE_ROUTE_GOSSIP = "continue_route_gossip"
    CONTINUE_LOW_LEASE_COVERAGE = "continue_low_lease_coverage"
    QUARANTINE_LEASE_FORK = "quarantine_lease_fork"
    QUARANTINE_UNLEASED_SELECTION = "quarantine_unleased_selection"
    QUARANTINE_CAPTURED_GOSSIP = "quarantine_captured_gossip"


@dataclass(frozen=True)
class LeaseRoutePolicy:
    min_leased_selected: int = 4
    min_lease_families: int = 3
    max_unleased_selected: int = 0
    min_work_bits: int = 0
    commit_on_stale_eviction: bool = True

    def validate(self) -> None:
        if self.min_leased_selected <= 0 or self.min_lease_families <= 0:
            raise ValueError("leased route thresholds must be positive")
        if self.max_unleased_selected < 0 or self.min_work_bits < 0:
            raise ValueError("lease route maxima/minima must be non-negative")


@dataclass(frozen=True)
class LeaseRouteDecision:
    kind: LeaseRouteDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class LeaseRouteReport:
    route_report: RouteGossipReport
    leased_selected: tuple[RouteContact, ...]
    unleased_selected: tuple[RouteContact, ...]
    live_route_leases: tuple[ContactLease, ...]
    lease_family_counts: dict[str, int]
    decision: LeaseRouteDecision
    transcript_digest: bytes

    @property
    def needs_more_evidence(self) -> bool:
        return not self.decision.accept


@dataclass
class LeaseRouteBook:
    route_book: RouteGossipBook
    lease_book: ContactLeaseBook

    @classmethod
    def empty(cls) -> "LeaseRouteBook":
        return cls(RouteGossipBook(), ContactLeaseBook())


def _copy_route_book(book: RouteGossipBook) -> RouteGossipBook:
    return RouteGossipBook(
        contacts=dict(book.contacts),
        quarantined_batches=set(book.quarantined_batches),
        evicted_node_ids=set(book.evicted_node_ids),
    )


def _commit_route_book(destination: RouteGossipBook, source: RouteGossipBook) -> None:
    destination.contacts = dict(source.contacts)
    destination.quarantined_batches = set(source.quarantined_batches)
    destination.evicted_node_ids = set(source.evicted_node_ids)


def _route_lease_counts(contacts: Iterable[RouteContact], leases_by_node: dict[bytes, ContactLease]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for contact in contacts:
        lease = leases_by_node.get(contact.node_id)
        if lease is None:
            continue
        counts[lease.family_id] = counts.get(lease.family_id, 0) + 1
    return counts


def assess_leased_route_gossip(
    book: LeaseRouteBook,
    batches: Iterable[RouteGossipBatch],
    leases: Iterable[ContactLease],
    *,
    now: int,
    route_policy: RouteGossipPolicy | None = None,
    lease_policy: LeaseRoutePolicy | None = None,
) -> LeaseRouteReport:
    """Assess route repair only after selected contacts have fresh route leases.

    The route book is only mutated on accepted leased repair.  Rejected reports
    remain useful evidence but do not silently populate local routing memory.
    """
    lease_policy = lease_policy or LeaseRoutePolicy()
    lease_policy.validate()
    route_policy = route_policy or RouteGossipPolicy()

    live_route_leases: list[ContactLease] = []
    for lease in leases:
        verdict = book.lease_book.observe(lease, now=now, min_work_bits=lease_policy.min_work_bits)
        if verdict.accepted and lease.has_purpose(ContactLeasePurpose.ROUTE):
            live_route_leases.append(lease)
    leases_by_node = {lease.node_id: lease for lease in live_route_leases}

    probe_book = _copy_route_book(book.route_book)
    route_report = probe_book.ingest_gossip(tuple(batches), now=now, policy=route_policy)
    leased_selected = tuple(contact for contact in route_report.selected_contacts if contact.node_id in leases_by_node)
    unleased_selected = tuple(contact for contact in route_report.selected_contacts if contact.node_id not in leases_by_node)
    lease_family_counts = _route_lease_counts(leased_selected, leases_by_node)

    if book.lease_book.fork_pressure:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.QUARANTINE_LEASE_FORK, False, "selected route evidence is tainted by same-sequence contact-lease fork pressure")
    elif route_report.decision.kind is RouteGossipDecisionKind.QUARANTINE_CAPTURED_GOSSIP:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.QUARANTINE_CAPTURED_GOSSIP, False, "route-gossip selection is introducer/family captured before lease evidence matters")
    elif len(unleased_selected) > lease_policy.max_unleased_selected:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.QUARANTINE_UNLEASED_SELECTION, False, "route gossip selected contacts without fresh route-purpose leases")
    elif not route_report.decision.accept:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.CONTINUE_ROUTE_GOSSIP, False, "route-gossip pressure still needs more diverse/fresh contacts")
    elif len(leased_selected) < lease_policy.min_leased_selected or len(lease_family_counts) < lease_policy.min_lease_families:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.CONTINUE_LOW_LEASE_COVERAGE, False, "accepted route gossip lacks enough fresh route leases across families")
    elif route_report.decision.kind is RouteGossipDecisionKind.EVICT_STALE_THEN_REPAIR:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.ACCEPT_EVICT_STALE_THEN_REPAIR, True, "stale route memory can be replaced by lease-backed diverse gossip")
    else:
        decision = LeaseRouteDecision(LeaseRouteDecisionKind.ACCEPT_LEASED_REPAIR, True, "route repair is fresh, lease-backed, and family-diverse enough")

    if decision.accept:
        _commit_route_book(book.route_book, probe_book)

    digest = sha256(LEASE_ROUTE_DOMAIN + b":report:" + bencode({
        b"route_report": route_report.transcript_digest,
        b"leased_selected": [contact.bvalue() for contact in leased_selected],
        b"unleased_selected": [contact.bvalue() for contact in unleased_selected],
        b"live_route_leases": [lease.lease_hash for lease in live_route_leases],
        b"lease_family_counts": {family.encode("utf-8"): count for family, count in sorted(lease_family_counts.items())},
        b"decision": decision.kind.value,
    }))
    return LeaseRouteReport(route_report, leased_selected, unleased_selected, tuple(live_route_leases), lease_family_counts, decision, digest)
