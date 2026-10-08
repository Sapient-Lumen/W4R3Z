"""Replication policy for a Kademlia-like DHT over I2P."""
from __future__ import annotations

from dataclasses import dataclass

from .ids import xor_distance
from .routing import Contact


@dataclass(frozen=True)
class ReplicationPolicy:
    k: int = 20
    alpha: int = 3
    beta: int = 3
    disjoint_paths: int = 3
    provider_ttl_seconds: int = 60 * 60
    mutable_ttl_seconds: int = 2 * 60 * 60
    immutable_cache_ttl_seconds: int = 24 * 60 * 60
    republish_interval_seconds: int = 45 * 60
    sloppy_cache_along_path: bool = True
    sloppy_extra_replicas: int = 3

    def validate(self) -> None:
        if self.k <= 0:
            raise ValueError("k must be positive")
        if self.alpha <= 0 or self.beta <= 0:
            raise ValueError("alpha and beta must be positive")
        if self.disjoint_paths <= 0:
            raise ValueError("disjoint_paths must be positive")

    def should_republish(self, *, last_publish_at: int, now: int) -> bool:
        return now - last_publish_at >= self.republish_interval_seconds


def select_replicas(contacts: list[Contact], target: bytes, *, policy: ReplicationPolicy, include_sloppy: bool = False) -> list[Contact]:
    policy.validate()
    count = policy.k + (policy.sloppy_extra_replicas if include_sloppy else 0)
    return sorted(contacts, key=lambda contact: xor_distance(contact.node_id, target))[:count]
