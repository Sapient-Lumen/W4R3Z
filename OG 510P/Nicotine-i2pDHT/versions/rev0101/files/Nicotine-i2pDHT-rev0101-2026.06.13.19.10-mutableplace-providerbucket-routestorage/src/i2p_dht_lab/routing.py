"""Kademlia/S-Kademlia-flavored routing table primitives."""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from .ids import bucket_index, xor_distance


@dataclass(frozen=True)
class Contact:
    node_id: bytes
    destination: str
    public_key: bytes = b""
    last_seen: int = 0
    rtt_ms: int | None = None
    failure_count: int = 0
    capabilities: tuple[str, ...] = ()
    work_bits: int = 0

    def refreshed(self, *, now: int, rtt_ms: int | None = None) -> "Contact":
        return replace(self, last_seen=now, rtt_ms=self.rtt_ms if rtt_ms is None else rtt_ms, failure_count=0)

    def failed(self) -> "Contact":
        return replace(self, failure_count=self.failure_count + 1)


@dataclass
class KBucket:
    k: int = 20
    replacement_cache_size: int = 10
    contacts: list[Contact] = field(default_factory=list)
    replacements: list[Contact] = field(default_factory=list)

    def insert(self, contact: Contact) -> str:
        """Insert or refresh a contact.

        Returns a small status string for tests and tracing:
        refreshed, inserted, queued_replacement, ignored_selfish_duplicate.
        """
        for index, existing in enumerate(self.contacts):
            if existing.node_id == contact.node_id:
                self.contacts.pop(index)
                self.contacts.append(contact)
                return "refreshed"
        if len(self.contacts) < self.k:
            self.contacts.append(contact)
            return "inserted"
        for index, existing in enumerate(self.replacements):
            if existing.node_id == contact.node_id:
                self.replacements.pop(index)
                self.replacements.append(contact)
                return "queued_replacement"
        self.replacements.append(contact)
        if len(self.replacements) > self.replacement_cache_size:
            self.replacements.pop(0)
        return "queued_replacement"

    def mark_failed(self, node_id: bytes, *, max_failures: int = 2) -> Contact | None:
        """Record a failure and promote a replacement if the contact is ejected."""
        for index, existing in enumerate(self.contacts):
            if existing.node_id != node_id:
                continue
            failed = existing.failed()
            if failed.failure_count < max_failures:
                self.contacts[index] = failed
                return None
            removed = self.contacts.pop(index)
            if self.replacements:
                self.contacts.append(self.replacements.pop())
            return removed
        return None


@dataclass
class RoutingTable:
    local_id: bytes
    k: int = 20
    replacement_cache_size: int = 10
    buckets: list[KBucket] = field(init=False)

    def __post_init__(self) -> None:
        self.buckets = [KBucket(k=self.k, replacement_cache_size=self.replacement_cache_size) for _ in range(len(self.local_id) * 8)]

    def insert(self, contact: Contact) -> str:
        idx = bucket_index(self.local_id, contact.node_id)
        if idx < 0:
            return "self_ignored"
        return self.buckets[idx].insert(contact)

    def mark_failed(self, node_id: bytes, *, max_failures: int = 2) -> Contact | None:
        idx = bucket_index(self.local_id, node_id)
        if idx < 0:
            return None
        return self.buckets[idx].mark_failed(node_id, max_failures=max_failures)

    def all_contacts(self) -> list[Contact]:
        contacts: list[Contact] = []
        for bucket in self.buckets:
            contacts.extend(bucket.contacts)
        return contacts

    def nearest(self, target_id: bytes, count: int = 8) -> list[Contact]:
        return sorted(self.all_contacts(), key=lambda c: xor_distance(c.node_id, target_id))[:count]

    def bucket_health(self) -> dict[str, int]:
        live = sum(len(bucket.contacts) for bucket in self.buckets)
        replacements = sum(len(bucket.replacements) for bucket in self.buckets)
        nonempty = sum(1 for bucket in self.buckets if bucket.contacts)
        return {"live_contacts": live, "replacement_contacts": replacements, "nonempty_buckets": nonempty}
