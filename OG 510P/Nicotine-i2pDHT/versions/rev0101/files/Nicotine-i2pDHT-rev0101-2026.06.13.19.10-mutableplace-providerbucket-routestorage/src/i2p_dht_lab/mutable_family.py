"""Mutable slot families beyond single-writer BEP44-style heads.

This module is mostly design scaffolding.  It encodes the guess that one DHT
should have several mutable shapes from birth, while keeping storage-node
validation simple and deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ids import DOMAIN, sha256


class MutableFamily(str, Enum):
    SINGLE_WRITER = "single_writer"       # BEP44/IPNS-like monotonic head
    DELEGATED = "delegated"               # long-term identity delegates a writer key
    MERKLE_FEED = "merkle_feed"           # append-ish log head; value points to root/tip
    CRDT_REGISTRY = "crdt_registry"       # multiwriter set/map summarized by a signed root


@dataclass(frozen=True)
class MutableSlotSpec:
    family: MutableFamily
    public_key: bytes
    salt: bytes = b""
    namespace: str = "generic"
    max_value_bytes: int = 1000
    quorum_hint: int = 12

    def validate(self) -> None:
        if len(self.public_key) != 32:
            raise ValueError("public_key must be 32 bytes")
        if len(self.salt) > 64:
            raise ValueError("salt must be <= 64 bytes")
        if not self.namespace:
            raise ValueError("namespace must not be empty")
        if self.max_value_bytes <= 0:
            raise ValueError("max_value_bytes must be positive")
        if self.quorum_hint <= 0:
            raise ValueError("quorum_hint must be positive")

    @property
    def target(self) -> bytes:
        self.validate()
        return sha256(
            DOMAIN
            + b":mutable-family-target:v1:"
            + self.family.value.encode("ascii")
            + b":"
            + self.namespace.encode("utf-8")
            + b":"
            + self.public_key
            + b":"
            + self.salt
        )

    @property
    def validator_name(self) -> str:
        return f"mutable.{self.family.value}.v1"
