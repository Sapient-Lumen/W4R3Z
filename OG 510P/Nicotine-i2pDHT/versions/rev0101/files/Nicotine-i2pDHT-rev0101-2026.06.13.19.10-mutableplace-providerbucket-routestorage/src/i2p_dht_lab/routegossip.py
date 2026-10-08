"""Route-gossip repair and stale-contact pressure lab.

A DHT above I2P will not have raw IP addresses, and long-lived I2P
Destinations make contact persistence tempting.  The risky guess is that cached
contacts and garden-provided gossip can repair routing tables after churn — but
also become a capture surface if one family keeps replaying stale or nearby
contacts.

This module models only local contact memory.  It is not a live routing table,
not a peer-profile system, and not a Sybil defense.  It gives tests a place to
ask: when should a node accept gossip, quarantine gossip, evict stale contacts,
or keep probing for more path/family diversity?
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .ids import DOMAIN, sha256, xor_distance

ROUTE_GOSSIP_DOMAIN = DOMAIN + b":route-gossip-v1:"


class RouteContactState(str, Enum):
    FRESH = "fresh"
    PROBATION = "probation"
    STALE = "stale"
    EVICTED = "evicted"
    QUARANTINED = "quarantined"


class RouteGossipDecisionKind(str, Enum):
    ACCEPT_REPAIR_CONTACTS = "accept_repair_contacts"
    CONTINUE_LOW_DIVERSITY = "continue_low_diversity"
    QUARANTINE_CAPTURED_GOSSIP = "quarantine_captured_gossip"
    EVICT_STALE_THEN_REPAIR = "evict_stale_then_repair"
    EMPTY = "empty"


@dataclass(frozen=True)
class RouteContact:
    node_id: bytes
    destination_hint: str
    family_id: str
    introduced_by: str
    first_seen_at: int
    last_seen_at: int
    success_count: int = 0
    failure_count: int = 0
    refusal_count: int = 0
    stale_after_seconds: int = 72 * 3600

    def __post_init__(self) -> None:
        if len(self.node_id) != 32:
            raise ValueError("route contact node_id must be 32 bytes")
        if not self.destination_hint or not self.family_id or not self.introduced_by:
            raise ValueError("route contact needs destination, family, and introducer")
        if self.last_seen_at < self.first_seen_at:
            raise ValueError("last_seen_at cannot precede first_seen_at")
        if self.success_count < 0 or self.failure_count < 0 or self.refusal_count < 0:
            raise ValueError("contact counters must be non-negative")
        if self.stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be positive")

    @property
    def score(self) -> int:
        return self.success_count * 8 + self.refusal_count - self.failure_count * 5

    def age_seconds(self, *, now: int) -> int:
        return max(0, now - self.last_seen_at)

    def state(self, *, now: int, failure_evict_threshold: int = 3) -> RouteContactState:
        if self.failure_count >= failure_evict_threshold:
            return RouteContactState.EVICTED
        if self.age_seconds(now=now) > self.stale_after_seconds:
            return RouteContactState.STALE
        if self.failure_count > self.success_count:
            return RouteContactState.PROBATION
        return RouteContactState.FRESH

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"destination_hint": self.destination_hint,
            b"family_id": self.family_id,
            b"introduced_by": self.introduced_by,
            b"first_seen_at": self.first_seen_at,
            b"last_seen_at": self.last_seen_at,
            b"success_count": self.success_count,
            b"failure_count": self.failure_count,
            b"refusal_count": self.refusal_count,
            b"stale_after_seconds": self.stale_after_seconds,
        }


@dataclass(frozen=True)
class RouteGossipBatch:
    issuer_node_id: bytes
    issuer_family: str
    target: bytes
    issued_at: int
    contacts: tuple[RouteContact, ...]
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.issuer_node_id) != 32 or len(self.target) != 32:
            raise ValueError("issuer and target must be 32-byte ids")
        if not self.issuer_family:
            raise ValueError("issuer family is required")

    @property
    def digest(self) -> bytes:
        return sha256(ROUTE_GOSSIP_DOMAIN + b":batch:" + bencode({
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_family": self.issuer_family,
            b"target": self.target,
            b"issued_at": self.issued_at,
            b"contacts": [contact.bvalue() for contact in self.contacts],
            b"note": self.note[:160],
        }))


@dataclass(frozen=True)
class RouteGossipPolicy:
    min_repair_contacts: int = 4
    min_repair_families: int = 3
    max_per_family: int = 2
    max_issuer_fraction: float = 0.50
    stale_after_seconds: int = 72 * 3600
    failure_evict_threshold: int = 3
    repair_limit: int = 8

    def validate(self) -> None:
        if self.min_repair_contacts <= 0 or self.min_repair_families <= 0 or self.max_per_family <= 0:
            raise ValueError("repair thresholds must be positive")
        if not 0.0 < self.max_issuer_fraction <= 1.0:
            raise ValueError("issuer fraction must be in (0, 1]")
        if self.stale_after_seconds <= 0 or self.failure_evict_threshold <= 0 or self.repair_limit <= 0:
            raise ValueError("stale/repair limits must be positive")


@dataclass(frozen=True)
class RouteGossipDecision:
    kind: RouteGossipDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class RouteGossipReport:
    target: bytes
    selected_contacts: tuple[RouteContact, ...]
    stale_evictions: tuple[RouteContact, ...]
    quarantined_contacts: tuple[RouteContact, ...]
    family_counts: dict[str, int]
    issuer_family_fraction: float
    transcript_digest: bytes
    decision: RouteGossipDecision

    @property
    def needs_more_gossip(self) -> bool:
        return not self.decision.accept

    @property
    def selected_family_count(self) -> int:
        return len(self.family_counts)


@dataclass
class RouteGossipBook:
    contacts: dict[bytes, RouteContact] = field(default_factory=dict)
    quarantined_batches: set[bytes] = field(default_factory=set)
    evicted_node_ids: set[bytes] = field(default_factory=set)

    def remember(self, contact: RouteContact) -> None:
        existing = self.contacts.get(contact.node_id)
        if existing is None or (contact.last_seen_at, contact.score) >= (existing.last_seen_at, existing.score):
            self.contacts[contact.node_id] = contact

    def observe_result(self, node_id: bytes, *, now: int, success: bool = False, failure: bool = False, useful_refusal: bool = False) -> None:
        contact = self.contacts.get(node_id)
        if contact is None:
            return
        updated = replace(
            contact,
            last_seen_at=now,
            success_count=contact.success_count + (1 if success else 0),
            failure_count=contact.failure_count + (1 if failure else 0),
            refusal_count=contact.refusal_count + (1 if useful_refusal else 0),
        )
        self.contacts[node_id] = updated

    def prune_stale(self, *, now: int, policy: RouteGossipPolicy | None = None) -> tuple[RouteContact, ...]:
        policy = policy or RouteGossipPolicy()
        policy.validate()
        evict: list[RouteContact] = []
        for node_id, contact in list(self.contacts.items()):
            state = contact.state(now=now, failure_evict_threshold=policy.failure_evict_threshold)
            if state in {RouteContactState.STALE, RouteContactState.EVICTED}:
                evict.append(contact)
                self.evicted_node_ids.add(node_id)
                del self.contacts[node_id]
        return tuple(evict)

    def ingest_gossip(self, batches: Iterable[RouteGossipBatch], *, now: int, policy: RouteGossipPolicy | None = None) -> RouteGossipReport:
        policy = policy or RouteGossipPolicy()
        policy.validate()
        stale = list(self.prune_stale(now=now, policy=policy))
        candidates: list[RouteContact] = []
        issuer_counts: dict[str, int] = {}
        all_batch_digests: list[bytes] = []
        first_target: bytes | None = None
        for batch in batches:
            if first_target is None:
                first_target = batch.target
            all_batch_digests.append(batch.digest)
            issuer_counts[batch.issuer_family] = issuer_counts.get(batch.issuer_family, 0) + len(batch.contacts)
            for contact in batch.contacts:
                if contact.state(now=now, failure_evict_threshold=policy.failure_evict_threshold) is RouteContactState.EVICTED:
                    continue
                if contact.state(now=now, failure_evict_threshold=policy.failure_evict_threshold) is RouteContactState.STALE:
                    stale.append(contact)
                    continue
                candidates.append(contact)

        if not candidates:
            digest = sha256(ROUTE_GOSSIP_DOMAIN + b":report:" + bencode({b"target": b"", b"batches": all_batch_digests, b"selected": []}))
            return RouteGossipReport(b"\x00" * 32, (), tuple(stale), (), {}, 0.0, digest, RouteGossipDecision(RouteGossipDecisionKind.EMPTY, False, "no fresh gossip contacts"))

        # Use the first batch target as the repair target; mixed-target batches are
        # still deterministic but should be avoided by callers.
        target = first_target or (b"\x00" * 32)
        # Prefer closer contacts, then better local score, then fresher contacts.
        selected = select_family_capped(
            candidates,
            family_of=lambda contact: contact.family_id,
            sort_key=lambda contact: (xor_distance(contact.node_id, target), -contact.score, -contact.last_seen_at, contact.node_id),
            limit=policy.repair_limit,
            max_per_family=policy.max_per_family,
        )
        family_counts: dict[str, int] = {}
        introduced_by_counts: dict[str, int] = {}
        for contact in selected:
            family_counts[contact.family_id] = family_counts.get(contact.family_id, 0) + 1
            introduced_by_counts[contact.introduced_by] = introduced_by_counts.get(contact.introduced_by, 0) + 1
        issuer_fraction = max(introduced_by_counts.values()) / len(selected) if selected else 0.0
        diversity = analyze_family_diversity(selected, family_of=lambda contact: contact.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_repair_families, max_per_family=policy.max_per_family))

        quarantined: tuple[RouteContact, ...] = ()
        if selected and issuer_fraction > policy.max_issuer_fraction and len(selected) >= policy.min_repair_contacts:
            quarantined = selected
            for digest in all_batch_digests:
                self.quarantined_batches.add(digest)
            decision = RouteGossipDecision(RouteGossipDecisionKind.QUARANTINE_CAPTURED_GOSSIP, False, "one introducer/family dominates selected repair gossip")
        elif len(stale) > 0 and len(selected) >= policy.min_repair_contacts and len(family_counts) >= policy.min_repair_families:
            decision = RouteGossipDecision(RouteGossipDecisionKind.EVICT_STALE_THEN_REPAIR, True, "stale contacts were evicted and enough diverse replacements exist")
        elif len(selected) < policy.min_repair_contacts or not diversity.passes(FamilyDiversityPolicy(min_families=policy.min_repair_families, max_per_family=policy.max_per_family)):
            decision = RouteGossipDecision(RouteGossipDecisionKind.CONTINUE_LOW_DIVERSITY, False, "repair gossip is not diverse enough")
        else:
            decision = RouteGossipDecision(RouteGossipDecisionKind.ACCEPT_REPAIR_CONTACTS, True, "repair gossip is diverse enough for local memory")

        if decision.accept:
            for contact in selected:
                self.remember(contact)

        digest = sha256(ROUTE_GOSSIP_DOMAIN + b":report:" + bencode({
            b"selected": [contact.bvalue() for contact in selected],
            b"stale": [contact.bvalue() for contact in stale],
            b"quarantined": [contact.bvalue() for contact in quarantined],
            b"family_counts": {family.encode("utf-8"): count for family, count in sorted(family_counts.items())},
            b"issuer_family_fraction": str(round(issuer_fraction, 4)),
            b"decision": decision.kind.value,
        }))
        return RouteGossipReport(target, selected, tuple(stale), quarantined, family_counts, issuer_fraction, digest, decision)
