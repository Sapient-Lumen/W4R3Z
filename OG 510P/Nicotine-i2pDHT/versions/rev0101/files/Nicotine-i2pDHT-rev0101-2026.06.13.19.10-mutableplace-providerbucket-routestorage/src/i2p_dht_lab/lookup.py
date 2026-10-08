"""Speculative lookup planning for an I2P-hosted Kademlia-like DHT.

The goal is not to implement a production network loop yet.  The goal is to
make the *shape* of future lookups testable: path isolation, quorum, careful
termination, and suspicion when independent paths disagree.  This is the part
of the DHT where we intentionally avoid the tempting but dangerous rule of
"stop as soon as somebody gives you enough-looking answers".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .ids import xor_distance, sha256
from .routing import Contact


class LookupKind(str, Enum):
    FIND_NODE = "find_node"
    GET_VALUE = "get_value"
    GET_PROVIDERS = "get_providers"
    GET_MUTABLE = "get_mutable"


@dataclass(frozen=True)
class LookupPolicy:
    """Tunables for future DHT lookups.

    * ``paths`` is the number of independent queues we try to preserve.
    * ``alpha_per_path`` is per-path fanout, not global fanout.
    * ``quorum`` is the number of distinct storage-node responses to prefer
      before accepting a mutable/value result.
    * ``min_honestish_paths`` says a result should be seen, confirmed, or at
      least not contradicted across several isolated paths before it is trusted.
    """

    k: int = 20
    paths: int = 4
    alpha_per_path: int = 2
    quorum: int = 12
    min_honestish_paths: int = 3
    max_rounds: int = 8
    allow_early_provider_stop: bool = False

    def validate(self) -> None:
        if self.k <= 0:
            raise ValueError("k must be positive")
        if self.paths <= 0:
            raise ValueError("paths must be positive")
        if self.alpha_per_path <= 0:
            raise ValueError("alpha_per_path must be positive")
        if self.quorum <= 0:
            raise ValueError("quorum must be positive")
        if self.min_honestish_paths <= 0 or self.min_honestish_paths > self.paths:
            raise ValueError("min_honestish_paths must be between 1 and paths")
        if self.max_rounds <= 0:
            raise ValueError("max_rounds must be positive")


@dataclass(frozen=True)
class PlannedQuery:
    contact: Contact
    path_index: int
    round_index: int = 0


@dataclass(frozen=True)
class LookupPath:
    index: int
    queue: tuple[Contact, ...]
    visited: tuple[bytes, ...] = ()

    def next_queries(self, *, alpha: int, round_index: int) -> tuple[PlannedQuery, ...]:
        visited = set(self.visited)
        selected: list[PlannedQuery] = []
        for contact in self.queue:
            if contact.node_id in visited:
                continue
            selected.append(PlannedQuery(contact=contact, path_index=self.index, round_index=round_index))
            if len(selected) >= alpha:
                break
        return tuple(selected)

    def with_contacts(self, contacts: Iterable[Contact], *, target: bytes, k: int) -> "LookupPath":
        by_id: dict[bytes, Contact] = {contact.node_id: contact for contact in self.queue}
        for contact in contacts:
            if contact.node_id not in self.visited:
                by_id[contact.node_id] = contact
        queue = tuple(sorted(by_id.values(), key=lambda c: xor_distance(c.node_id, target))[:k])
        return LookupPath(index=self.index, queue=queue, visited=self.visited)

    def mark_visited(self, node_ids: Iterable[bytes]) -> "LookupPath":
        seen = list(self.visited)
        present = set(seen)
        for node_id in node_ids:
            if node_id not in present:
                seen.append(node_id)
                present.add(node_id)
        return LookupPath(index=self.index, queue=self.queue, visited=tuple(seen))


def contact_diversity_key(contact: Contact, *, bytes_wide: int = 2) -> bytes:
    """Return a stable bucketing key for path diversity.

    I2P hides IP neighborhoods from us, so an IPv4-/16-style diversity rule is
    unavailable.  This is only a guess: diversify by a hash of the advertised
    Destination plus node-id so a single visible identity cannot trivially occupy
    every path with identical contact material.
    """

    material = contact.destination.encode("utf-8") + b"\0" + contact.node_id
    return sha256(b"i2p-dht-lab:path-diversity:v1:" + material)[:bytes_wide]


def split_disjoint_paths(contacts: Iterable[Contact], target: bytes, *, policy: LookupPolicy) -> tuple[LookupPath, ...]:
    """Split contacts into distance-ordered, diversity-aware lookup paths."""

    policy.validate()
    ordered = sorted(contacts, key=lambda c: xor_distance(c.node_id, target))
    buckets: list[list[Contact]] = [[] for _ in range(policy.paths)]
    used_diversity: list[set[bytes]] = [set() for _ in range(policy.paths)]

    for contact in ordered:
        diversity_key = contact_diversity_key(contact)
        ranked_paths = sorted(range(policy.paths), key=lambda idx: (len(buckets[idx]), idx))
        chosen = ranked_paths[0]
        for idx in ranked_paths:
            if diversity_key not in used_diversity[idx]:
                chosen = idx
                break
        buckets[chosen].append(contact)
        used_diversity[chosen].add(diversity_key)

    return tuple(LookupPath(index=i, queue=tuple(bucket[: policy.k])) for i, bucket in enumerate(buckets))


@dataclass(frozen=True)
class PathObservation:
    path_index: int
    responders: frozenset[bytes] = frozenset()
    closer_nodes_returned: int = 0
    value_digest: bytes | None = None
    provider_digests: frozenset[bytes] = frozenset()
    empty_response: bool = False
    contradiction: bool = False


@dataclass(frozen=True)
class LookupDecision:
    accept: bool
    reason: str
    confidence: str
    responding_paths: int
    quorum_count: int
    suspected_eclipse: bool = False


def decide_lookup_acceptance(observations: Iterable[PathObservation], *, policy: LookupPolicy, kind: LookupKind) -> LookupDecision:
    """Return a conservative-by-default decision from path-isolated evidence.

    For provider lookups, the design intentionally does not stop at the first N
    provider answers unless ``allow_early_provider_stop`` is explicitly enabled.
    That models the IPFS lesson that early termination can become an eclipse
    primitive when Sybils return semantically plausible but false provider sets.
    """

    policy.validate()
    observations = tuple(observations)
    responding_paths = len({obs.path_index for obs in observations if obs.responders or obs.empty_response})
    quorum_count = sum(len(obs.responders) for obs in observations)
    contradiction_paths = sum(1 for obs in observations if obs.contradiction)
    empty_paths = sum(1 for obs in observations if obs.empty_response and not obs.responders)
    suspected_eclipse = contradiction_paths > 0 or (empty_paths >= max(2, policy.paths // 2) and quorum_count < policy.quorum)

    if responding_paths < policy.min_honestish_paths:
        return LookupDecision(False, "insufficient_path_diversity", "low", responding_paths, quorum_count, suspected_eclipse)
    if quorum_count < policy.quorum:
        return LookupDecision(False, "insufficient_quorum", "medium" if not suspected_eclipse else "low", responding_paths, quorum_count, suspected_eclipse)
    if kind is LookupKind.GET_PROVIDERS and not policy.allow_early_provider_stop and responding_paths < policy.paths:
        return LookupDecision(False, "provider_lookup_should_finish_all_paths", "medium", responding_paths, quorum_count, suspected_eclipse)
    if suspected_eclipse:
        return LookupDecision(False, "possible_eclipse_or_poisoning", "low", responding_paths, quorum_count, suspected_eclipse)
    return LookupDecision(True, "accepted_by_quorum_and_path_diversity", "high", responding_paths, quorum_count, suspected_eclipse)


@dataclass
class LookupTrace:
    """Tiny mutable trace object for deterministic simulations."""

    target: bytes
    policy: LookupPolicy
    paths: tuple[LookupPath, ...]
    round_index: int = 0
    history: list[PlannedQuery] = field(default_factory=list)

    @classmethod
    def start(cls, contacts: Iterable[Contact], target: bytes, *, policy: LookupPolicy) -> "LookupTrace":
        return cls(target=target, policy=policy, paths=split_disjoint_paths(contacts, target, policy=policy))

    def next_round(self) -> tuple[PlannedQuery, ...]:
        if self.round_index >= self.policy.max_rounds:
            return ()
        queries: list[PlannedQuery] = []
        for path in self.paths:
            queries.extend(path.next_queries(alpha=self.policy.alpha_per_path, round_index=self.round_index))
        self.history.extend(queries)
        visited_by_path: dict[int, list[bytes]] = {}
        for query in queries:
            visited_by_path.setdefault(query.path_index, []).append(query.contact.node_id)
        new_paths = []
        for path in self.paths:
            new_paths.append(path.mark_visited(visited_by_path.get(path.index, [])))
        self.paths = tuple(new_paths)
        self.round_index += 1
        return tuple(queries)
